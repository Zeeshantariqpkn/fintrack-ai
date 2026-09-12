"""
Categorization Agent.

Classifies every transaction into one of the fixed categories. Uses Groq when
available; falls back to deterministic keyword matching.
"""
from __future__ import annotations

import json
from typing import Any, Dict, List

import pandas as pd

from agents.strategic_agents import call_hf, hf_available, _safe_json

CATEGORIES: List[str] = [
    "Payroll",
    "Vendors",
    "Utilities",
    "Marketing",
    "Subscriptions",
    "Rent",
    "Income",
    "Other",
]

_CATEGORY_SET = set(CATEGORIES)

_KEYWORDS: Dict[str, List[str]] = {
    "Payroll": [
        "payroll", "salary", "salaries", "wage", "wages", "gusto", "adp",
        "paychex", "compensation", "bonus", "contractor", "freelance",
    ],
    "Rent": ["rent", "lease", "wework", "office space", "property", "landlord"],
    "Utilities": [
        "utility", "utilities", "electric", "electricity", "water", "gas",
        "internet", "pg&e", "pge", "comcast", "verizon", "at&t", "att",
        "phone", "mobile",
    ],
    "Marketing": [
        "ads", "advertising", "marketing", "google ads", "facebook ads",
        "facebook", "meta ads", "instagram", "tiktok", "linkedin ads",
        "campaign", "seo", "promotion", "hubspot", "mailchimp",
    ],
    "Subscriptions": [
        "subscription", "notion", "slack", "figma", "adobe", "zoom",
        "github", "dropbox", "spotify", "netflix", "saas", "license",
        "creative cloud", "canva", "crm",
    ],
    "Vendors": [
        "aws", "amazon web services", "azure", "gcp", "google cloud",
        "hosting", "server", "cloud", "supplier", "vendor", "inventory",
        "shipping", "logistics", "stripe fees", "paypal fees",
    ],
    "Income": [
        "stripe payout", "payout", "revenue", "income", "sales", "invoice",
        "customer", "client", "deposit", "shopify payout", "payment received",
    ],
}


def _keyword_category(description: str, amount: float) -> tuple[str, float]:
    desc = (description or "").lower()
    if amount >= 0 and not any(k in desc for k in _KEYWORDS["Income"]):
        return "Income", 0.55

    best_cat = "Other"
    best_score = 0
    for cat, kws in _KEYWORDS.items():
        for kw in kws:
            if kw in desc:
                score = len(kw.split()) * 2 + 1
                if score > best_score:
                    best_score = score
                    best_cat = cat

    if best_cat == "Other":
        if amount >= 0:
            return "Income", 0.4
        return "Other", 0.35

    confidence = min(0.95, 0.55 + best_score * 0.08)
    return best_cat, confidence


def _llm_categorize_batch(batch: List[Dict[str, Any]]) -> Dict[str, str]:
    if not hf_available():
        return {}
    prompt = (
        "You are a financial transaction categorizer. Categorize each transaction "
        "into EXACTLY ONE of these categories: "
        f"{', '.join(CATEGORIES)}.\n"
        "Respond ONLY with a JSON object mapping transaction_id to category.\n\n"
        f"Transactions:\n{json.dumps(batch)[:3500]}\n\nJSON:"
    )
    text = call_hf(prompt, max_new_tokens=500, temperature=0.1)
    parsed = _safe_json(text)
    if not isinstance(parsed, dict):
        return {}
    cleaned: Dict[str, str] = {}
    for k, v in parsed.items():
        if isinstance(v, str):
            for cat in CATEGORIES:
                if cat.lower() == v.strip().lower():
                    cleaned[str(k)] = cat
                    break
    return cleaned


def run_categorization_agent(
    df: pd.DataFrame,
    use_ai: bool = True,
    batch_size: int = 12,
) -> Dict[str, Any]:
    df = df.copy()
    categories: List[str] = []
    confidences: List[float] = []
    used_ai = 0
    used_kw = 0

    ai_map: Dict[str, str] = {}
    if use_ai and hf_available():
        for i in range(0, len(df), batch_size):
            chunk = df.iloc[i : i + batch_size]
            batch = [
                {
                    "transaction_id": row["transaction_id"],
                    "description": str(row["description"])[:120],
                    "amount": float(row["amount"]),
                }
                for _, row in chunk.iterrows()
            ]
            ai_map.update(_llm_categorize_batch(batch))

    for _, row in df.iterrows():
        tid = row["transaction_id"]
        desc = str(row["description"])
        amt = float(row["amount"])

        kw_cat, kw_conf = _keyword_category(desc, amt)

        if tid in ai_map:
            categories.append(ai_map[tid])
            confidences.append(0.85)
            used_ai += 1
        else:
            categories.append(kw_cat)
            confidences.append(kw_conf)
            used_kw += 1

    df["category"] = categories
    df["category_confidence"] = confidences

    df["category"] = df["category"].apply(lambda c: c if c in _CATEGORY_SET else "Other")

    counts = df["category"].value_counts().to_dict()

    if used_ai and used_kw:
        method = "hybrid"
    elif used_ai:
        method = "ai"
    else:
        method = "keyword"

    return {
        "df": df,
        "counts": {str(k): int(v) for k, v in counts.items()},
        "method": method,
        "classified": int(len(df)),
        "ai_classified": used_ai,
        "keyword_classified": used_kw,
    }
