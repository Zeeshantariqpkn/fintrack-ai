"""Financial Insight and Chat Agent using Hugging Face with deterministic fallbacks."""

import os

from huggingface_hub import InferenceClient


MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"


def _stats_to_text(stats: dict) -> str:
    """Convert calculated statistics into a compact text context."""

    lines = [
        f"Total income: {stats['total_income']:.2f}",
        f"Total expense: {stats['total_expense']:.2f}",
    ]

    # Spending by category
    if stats["by_category"] is not None:

        lines.append("Spend by category:")

        for category, amount in stats[
            "by_category"
        ].items():

            lines.append(
                f"- {category}: {amount:.2f}"
            )

    # Monthly performance
    lines.append(
        "Monthly income vs expense:"
    )

    lines.append(
        stats["monthly"].to_string()
    )

    # Top vendors
    lines.append(
        "Top vendors by spend:"
    )

    for vendor, amount in stats[
        "top_vendors"
    ].items():

        lines.append(
            f"- {vendor}: {amount:.2f}"
        )

    # Recurring expenses
    if len(stats["recurring"]) > 0:

        lines.append(
            "Recurring charges:"
        )

        for description, count in stats[
            "recurring"
        ].items():

            lines.append(
                f"- {description}: seen in {count} months"
            )

    return "\n".join(lines)


def _call_llm(prompt: str) -> str:
    """Call Hugging Face. Return empty string if unavailable."""

    token = os.environ.get("HF_TOKEN")

    if not token:
        return ""

    try:

        client = InferenceClient(
            model=MODEL_NAME,
            token=token,
        )

        response = client.chat_completion(
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            max_tokens=500,
            temperature=0.2,
        )

        return (
            response
            .choices[0]
            .message
            .content
            .strip()
        )

    except Exception as exc:

        print(
            f"[insights] Hugging Face failed: {exc}"
        )

        return ""


def _fallback_summary(stats: dict) -> str:
    """Generate financial summary without an AI API."""

    income = stats["total_income"]

    expense = stats["total_expense"]

    net = income - expense

    if income > 0:

        expense_ratio = (
            expense / income
        ) * 100

    else:

        expense_ratio = 0

    lines = [
        "### Financial Overview",
        f"- Total income: **${income:,.2f}**",
        f"- Total expenses: **${expense:,.2f}**",
        f"- Net cash flow: **${net:,.2f}**",
        (
            f"- Expense-to-income ratio: "
            f"**{expense_ratio:.1f}%**"
        ),
    ]

    # Financial health warning
    if net < 0:

        lines.append(
            "⚠️ **Warning:** Expenses are higher than income."
        )

    elif expense_ratio > 80:

        lines.append(
            "⚠️ **Warning:** Expenses consume "
            "a large portion of income."
        )

    else:

        lines.append(
            "✅ **Healthy sign:** Income currently "
            "exceeds expenses."
        )

    # Highest category
    if (
        stats["by_category"] is not None
        and len(stats["by_category"]) > 0
    ):

        category = (
            stats["by_category"]
            .index[0]
        )

        amount = (
            stats["by_category"]
            .iloc[0]
        )

        lines.append(
            f"📊 Highest spending category: "
            f"**{category} (${amount:,.2f})**"
        )

    # Highest vendor
    if len(stats["top_vendors"]) > 0:

        vendor = (
            stats["top_vendors"]
            .index[0]
        )

        amount = (
            stats["top_vendors"]
            .iloc[0]
        )

        lines.append(
            f"🏢 Highest-spend vendor: "
            f"**{vendor} (${amount:,.2f})**"
        )

    # Recurring expenses
    if len(stats["recurring"]) > 0:

        lines.append(
            f"🔁 Detected **{len(stats['recurring'])} "
            f"recurring charges**."
        )

    return "\n".join(lines)


def generate_summary(stats: dict) -> str:
    """Generate an AI-powered financial summary."""

    financial_context = _stats_to_text(
        stats
    )

    prompt = f"""
You are FinTrack AI, an AI financial analyst
for small businesses.

Analyze ONLY the following computed financial
statistics:

{financial_context}

Write a concise 3-5 sentence financial health summary.

Your response should mention:

1. Cash flow
2. Largest spending area
3. One important risk or pattern
4. One practical recommendation

Use actual numbers from the provided data.

Do NOT invent information.

Do NOT provide investment or legal advice.
"""

    result = _call_llm(prompt)

    if result:

        return result

    return _fallback_summary(stats)


def answer_question(
    stats: dict,
    question: str,
) -> str:
    """Answer a user's financial question."""

    financial_context = _stats_to_text(
        stats
    )

    prompt = f"""
You are FinTrack AI, a financial analytics
assistant for small businesses.

Answer the user's question using ONLY the
following computed financial statistics:

{financial_context}

User question:

{question}

Rules:

- Be concise.
- Use actual numbers.
- Never invent data.
- Do not provide investment or legal advice.
- If the requested information is unavailable,
  say so clearly.
"""

    result = _call_llm(prompt)

    if result:

        return result

    # ---------------------------------------
    # Deterministic fallback answers
    # ---------------------------------------

    q = question.lower()

    # Highest vendor
    if (
        "vendor" in q
        and (
            "most" in q
            or "highest" in q
            or "largest" in q
        )
        and len(stats["top_vendors"]) > 0
    ):

        vendor = (
            stats["top_vendors"]
            .index[0]
        )

        amount = (
            stats["top_vendors"]
            .iloc[0]
        )

        return (
            f"The highest-spend vendor/"
            f"description is **{vendor}**, "
            f"with **${amount:,.2f}** in spending."
        )

    # Income
    if (
        "income" in q
        or "revenue" in q
    ):

        return (
            f"Total income is "
            f"**${stats['total_income']:,.2f}**."
        )

    # Expenses
    if (
        "expense" in q
        or "expenses" in q
        or "spending" in q
        or "spent" in q
    ):

        return (
            f"Total expenses are "
            f"**${stats['total_expense']:,.2f}**."
        )

    # Recurring expenses
    if (
        "recurring" in q
        or "subscription" in q
    ):

        return (
            f"I detected **{len(stats['recurring'])} "
            f"recurring charges**."
        )

    # Cash flow
    if (
        "cash flow" in q
        or "cashflow" in q
        or "net" in q
        or "profit" in q
    ):

        net = (
            stats["total_income"]
            - stats["total_expense"]
        )

        return (
            f"Your net cash flow is "
            f"**${net:,.2f}** "
            f"based on the available transactions."
        )

    return (
        "The AI model is unavailable right now. "
        "Try asking about income, expenses, "
        "vendors, recurring charges, or cash flow."
    )