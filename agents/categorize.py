"""Transaction Categorization Agent using Hugging Face with a deterministic fallback."""

import json
import os

import pandas as pd
from huggingface_hub import InferenceClient


CATEGORIES = [
    "Payroll",
    "Vendors",
    "Utilities",
    "Marketing",
    "Subscriptions",
    "Rent",
    "Income",
    "Other",
]


KEYWORD_MAP = {
    "payroll": "Payroll",
    "salary": "Payroll",

    "rent": "Rent",

    "electricity": "Utilities",
    "water bill": "Utilities",
    "water": "Utilities",
    "internet": "Utilities",

    "ads": "Marketing",
    "campaign": "Marketing",
    "facebook": "Marketing",
    "instagram": "Marketing",
    "google ads": "Marketing",

    "subscription": "Subscriptions",
    "zoom": "Subscriptions",
    "slack": "Subscriptions",
    "notion": "Subscriptions",
    "adobe": "Subscriptions",

    "vendor": "Vendors",
    "supplies": "Vendors",
    "aws": "Vendors",
    "staples": "Vendors",
    "techparts": "Vendors",
    "paperplus": "Vendors",

    "client payment": "Income",
}


def _keyword_categorize(
    description: str,
    amount: float,
) -> str:

    # Positive transactions are income
    if amount > 0:
        return "Income"

    description_lower = description.lower()

    for keyword, category in KEYWORD_MAP.items():

        if keyword in description_lower:
            return category

    return "Other"


def _call_llm_batch(
    transactions: list[dict],
) -> dict:

    token = os.environ.get("HF_TOKEN")

    if not token:
        return {}

    try:

        client = InferenceClient(
            model="Qwen/Qwen2.5-7B-Instruct",
            token=token,
        )

        prompt = f"""
You are a financial transaction categorization agent.

Categorize every transaction into exactly one
of these allowed categories:

{", ".join(CATEGORIES)}

Transactions:

{json.dumps(
    transactions,
    indent=2,
    default=str
)}

Return ONLY valid JSON.

The JSON must map each transaction ID
to exactly one category.

Example:

{{
    "0": "Payroll",
    "1": "Vendors",
    "2": "Marketing"
}}

Do not add explanations.
Do not create new categories.
"""

        response = client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=1000,
            temperature=0.1,
        )

        text = response.choices[0].message.content.strip()

        # Remove markdown code fences if the model adds them
        text = text.replace(
            "```json",
            "",
        )

        text = text.replace(
            "```",
            "",
        )

        text = text.strip()

        result = json.loads(text)

        if isinstance(result, dict):
            return result

        return {}

    except Exception as exc:

        print(
            f"[categorize] Hugging Face failed: {exc}"
        )

        return {}


def categorize_transactions(
    df: pd.DataFrame,
    batch_size: int = 25,
    use_llm: bool = True,
) -> pd.DataFrame:

    """
    Categorize financial transactions.

    Hugging Face is used when HF_TOKEN is available.
    If Hugging Face fails or is unavailable,
    keyword-based categorization is used automatically.
    """

    df = df.reset_index(
        drop=True
    ).copy()

    categories = [None] * len(df)

    # ---------------------------------------
    # Hugging Face categorization
    # ---------------------------------------
    if (
        use_llm
        and os.environ.get("HF_TOKEN")
    ):

        for start in range(
            0,
            len(df),
            batch_size,
        ):

            batch = df.iloc[
                start:start + batch_size
            ]

            payload = []

            for i, row in batch.iterrows():

                payload.append(
                    {
                        "id": int(i),
                        "description": row[
                            "description"
                        ],
                        "amount": float(
                            row["amount"]
                        ),
                    }
                )

            result = _call_llm_batch(
                payload
            )

            for i in batch.index:

                category = result.get(
                    str(i)
                )

                if category in CATEGORIES:

                    categories[i] = category

    # ---------------------------------------
    # Deterministic fallback
    # ---------------------------------------
    for i, row in df.iterrows():

        if not categories[i]:

            categories[i] = (
                _keyword_categorize(
                    row["description"],
                    row["amount"],
                )
            )

    df["category"] = categories

    return df