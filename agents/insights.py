"""
Insight Agent for FinTrack AI.

This agent takes financial analytics plus the output of the
Decision Agent and turns them into a concise financial
explanation for the business owner.
"""

import os

from huggingface_hub import InferenceClient


MODEL_NAME = "Qwen/Qwen2.5-7B-Instruct"


def _stats_to_text(stats: dict) -> str:
    """Convert financial statistics into LLM-readable context."""

    lines = [
        f"Total income: ${stats['total_income']:,.2f}",
        f"Total expenses: ${stats['total_expense']:,.2f}",
    ]

    net_cash_flow = (
        stats["total_income"]
        - stats["total_expense"]
    )

    lines.append(
        f"Net cash flow: ${net_cash_flow:,.2f}"
    )

    if stats["total_income"] > 0:

        expense_ratio = (
            stats["total_expense"]
            / stats["total_income"]
        ) * 100

    else:

        expense_ratio = 0

    lines.append(
        f"Expense ratio: {expense_ratio:.1f}%"
    )

    # Spending categories
    if (
        stats["by_category"] is not None
        and len(stats["by_category"]) > 0
    ):

        lines.append(
            "Spending by category:"
        )

        for category, amount in (
            stats["by_category"].items()
        ):

            lines.append(
                f"- {category}: ${amount:,.2f}"
            )

    # Monthly performance
    lines.append(
        "Monthly income and expenses:"
    )

    lines.append(
        stats["monthly"].to_string()
    )

    # Top vendors
    if len(stats["top_vendors"]) > 0:

        lines.append(
            "Top vendors/descriptions:"
        )

        for vendor, amount in (
            stats["top_vendors"].items()
        ):

            lines.append(
                f"- {vendor}: ${amount:,.2f}"
            )

    # Recurring expenses
    if len(stats["recurring"]) > 0:

        lines.append(
            "Recurring expenses:"
        )

        for description, count in (
            stats["recurring"].items()
        ):

            lines.append(
                f"- {description}: "
                f"appears in {count} months"
            )

    return "\n".join(lines)


def _decision_to_text(
    decision: dict,
) -> str:
    """Convert Decision Agent output into LLM context."""

    lines = [
        "Financial Health Score: "
        f"{decision.get('health_score', 0)}/100",
        "Financial Status: "
        f"{decision.get('status', 'Unknown')}",
        "Transaction Count: "
        f"{decision.get('transaction_count', 0)}",
    ]

    # Risks
    risks = decision.get(
        "risks",
        [],
    )

    if risks:

        lines.append("Detected Risks:")

        for risk in risks:

            lines.append(
                f"- {risk.get('title')}: "
                f"{risk.get('description')}"
            )

    # Opportunities
    opportunities = decision.get(
        "opportunities",
        [],
    )

    if opportunities:

        lines.append(
            "Detected Opportunities:"
        )

        for opportunity in opportunities:

            lines.append(
                f"- {opportunity.get('title')}: "
                f"{opportunity.get('description')}"
            )

    # Recommendations
    recommendations = decision.get(
        "recommendations",
        [],
    )

    if recommendations:

        lines.append(
            "Recommended Actions:"
        )

        for recommendation in recommendations:

            lines.append(
                f"- {recommendation}"
            )

    return "\n".join(lines)


def _call_llm(prompt: str) -> str:
    """Call Hugging Face and safely handle failures."""

    token = os.environ.get(
        "HF_TOKEN"
    )

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
            max_tokens=600,
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


def _fallback_summary(
    stats: dict,
    decision: dict,
) -> str:
    """
    Generate a useful summary without an LLM.

    This guarantees the hackathon demo still works
    if Hugging Face is unavailable.
    """

    income = stats[
        "total_income"
    ]

    expense = stats[
        "total_expense"
    ]

    net = income - expense

    expense_ratio = (
        (expense / income) * 100
        if income > 0
        else 0
    )

    health_score = decision.get(
        "health_score",
        0,
    )

    status = decision.get(
        "status",
        "Unknown",
    )

    lines = [
        "### 🧠 FinTrack AI Decision Summary",
        "",
        (
            f"**Financial health:** "
            f"{health_score}/100 — {status}."
        ),
        (
            f"Income is **${income:,.2f}** "
            f"against expenses of "
            f"**${expense:,.2f}**, producing "
            f"net cash flow of **${net:,.2f}**."
        ),
        (
            f"Expenses currently represent "
            f"**{expense_ratio:.1f}%** of income."
        ),
    ]

    # Largest category
    by_category = stats.get(
        "by_category"
    )

    if (
        by_category is not None
        and len(by_category) > 0
    ):

        category = by_category.index[0]

        amount = by_category.iloc[0]

        lines.append(
            f"The largest spending category is "
            f"**{category}** at "
            f"**${amount:,.2f}**."
        )

    # Risks
    risks = decision.get(
        "risks",
        [],
    )

    if risks:

        lines.append(
            f"⚠️ **Key risk:** "
            f"{risks[0].get('description')}"
        )

    # Opportunity
    opportunities = decision.get(
        "opportunities",
        [],
    )

    if opportunities:

        lines.append(
            f"💡 **Opportunity:** "
            f"{opportunities[0].get('description')}"
        )

    # Recommendation
    recommendations = decision.get(
        "recommendations",
        [],
    )

    if recommendations:

        lines.append(
            f"🎯 **Recommended action:** "
            f"{recommendations[0]}"
        )

    return "\n".join(lines)


def generate_summary(
    stats: dict,
    decision: dict | None = None,
) -> str:
    """
    Generate an AI-powered financial decision summary.

    The LLM receives BOTH:
    1. Analytics Agent output
    2. Decision Agent output
    """

    if decision is None:

        decision = {}

    financial_context = _stats_to_text(
        stats
    )

    decision_context = _decision_to_text(
        decision
    )

    prompt = f"""
You are FinTrack AI's Senior Financial
Insight Agent.

You are part of an agentic financial
analysis pipeline.

The Analytics Agent calculated:

{financial_context}

The Decision Agent evaluated the data:

{decision_context}

Your task is to explain the business situation
to a small-business owner.

Produce a concise but useful financial briefing.

Include:

1. Overall financial health
2. Most important spending pattern
3. Biggest risk
4. Best opportunity
5. One practical action the owner should take

Use the actual numbers provided.

Do not invent information.

Do not provide investment, tax, accounting,
or legal advice.

Make the answer easy for a non-financial expert
to understand.
"""

    result = _call_llm(prompt)

    if result:

        return result

    return _fallback_summary(
        stats,
        decision,
    )


def answer_question(
    stats: dict,
    question: str,
    decision: dict | None = None,
) -> str:
    """
    Answer a financial question using both
    analytics and decision-agent context.
    """

    if decision is None:

        decision = {}

    financial_context = _stats_to_text(
        stats
    )

    decision_context = _decision_to_text(
        decision
    )

    prompt = f"""
You are FinTrack AI's Financial Chat Agent.

Analytics Agent output:

{financial_context}

Decision Agent output:

{decision_context}

User question:

{question}

Answer using ONLY the information above.

Rules:

- Be concise.
- Use actual numbers.
- Explain the reasoning clearly.
- Never invent data.
- Do not provide investment, tax,
  accounting or legal advice.
- If the information is unavailable,
  say so clearly.
"""

    result = _call_llm(prompt)

    if result:

        return result

    # ---------------------------------------
    # Deterministic fallback
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

        count = len(
            stats["recurring"]
        )

        return (
            f"I detected **{count} recurring "
            f"expense patterns**."
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
            f"Net cash flow is "
            f"**${net:,.2f}**."
        )

    # Financial health
    if (
        "health" in q
        or "risk" in q
    ):

        score = decision.get(
            "health_score",
            0,
        )

        status = decision.get(
            "status",
            "Unknown",
        )

        return (
            f"FinTrack AI's financial health "
            f"score is **{score}/100** "
            f"({status})."
        )

    # Recommendation
    if (
        "recommend" in q
        or "recommendation" in q
        or "should i" in q
        or "what should" in q
    ):

        recommendations = decision.get(
            "recommendations",
            [],
        )

        if recommendations:

            return (
                "My main recommendation is: "
                f"**{recommendations[0]}**"
            )

    return (
        "I could not determine the answer "
        "from the available financial data. "
        "Try asking about income, expenses, "
        "vendors, recurring costs, cash flow, "
        "financial health, risks, or recommendations."
    )