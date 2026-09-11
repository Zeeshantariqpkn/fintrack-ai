"""
Decision Agent for FinTrack AI.

This agent takes the outputs of the analytics pipeline and
turns financial patterns into risks, opportunities and
practical business recommendations.
"""

from typing import Any

import pandas as pd


def _safe_float(value: Any) -> float:
    """Safely convert a value to float."""

    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def run_decision_agent(
    df: pd.DataFrame,
    stats: dict,
) -> dict:
    """
    Analyze financial statistics and generate
    business-level decisions.

    Returns:
        {
            "health_score": int,
            "status": str,
            "risks": list,
            "opportunities": list,
            "recommendations": list,
            "positive_signals": list,
            "findings": list,
        }
    """

    income = _safe_float(
        stats.get("total_income", 0)
    )

    expense = _safe_float(
        stats.get("total_expense", 0)
    )

    net_cash_flow = income - expense

    if income > 0:
        expense_ratio = (
            expense / income
        ) * 100
    else:
        expense_ratio = 100.0

    # ---------------------------------------
    # Financial Health Score
    # ---------------------------------------

    if income <= 0:

        health_score = 20

    elif net_cash_flow < 0:

        health_score = 35

    elif expense_ratio > 80:

        health_score = 60

    elif expense_ratio > 65:

        health_score = 75

    else:

        health_score = 90

    if health_score >= 80:

        status = "Healthy"

    elif health_score >= 60:

        status = "Moderate Risk"

    else:

        status = "High Risk"

    risks = []
    opportunities = []
    recommendations = []
    positive_signals = []
    findings = []

    # ---------------------------------------
    # Rule 1: Negative cash flow
    # ---------------------------------------

    if net_cash_flow < 0:

        risks.append(
            {
                "title": "Negative Cash Flow",
                "description": (
                    f"Expenses exceed income by "
                    f"${abs(net_cash_flow):,.2f}."
                ),
                "severity": "High",
            }
        )

        recommendations.append(
            "Review discretionary spending and "
            "reduce non-essential expenses."
        )

        findings.append(
            {
                "type": "Risk",
                "title": "Cash Flow Deficit",
                "description": (
                    "The business is spending more "
                    "than it is receiving."
                ),
            }
        )

    else:

        positive_signals.append(
            {
                "title": "Positive Cash Flow",
                "description": (
                    f"Income exceeds expenses by "
                    f"${net_cash_flow:,.2f}."
                ),
            }
        )

        findings.append(
            {
                "type": "Positive",
                "title": "Positive Cash Flow",
                "description": (
                    f"Net cash flow is "
                    f"${net_cash_flow:,.2f}."
                ),
            }
        )

    # ---------------------------------------
    # Rule 2: High expense ratio
    # ---------------------------------------

    if expense_ratio > 80:

        risks.append(
            {
                "title": "High Expense Ratio",
                "description": (
                    f"Expenses consume "
                    f"{expense_ratio:.1f}% "
                    f"of income."
                ),
                "severity": "High",
            }
        )

        recommendations.append(
            "Identify the fastest-growing expense "
            "categories before increasing spending."
        )

    elif expense_ratio > 65:

        risks.append(
            {
                "title": "Rising Cost Pressure",
                "description": (
                    f"Expenses consume "
                    f"{expense_ratio:.1f}% "
                    f"of income."
                ),
                "severity": "Medium",
            }
        )

        recommendations.append(
            "Monitor monthly expense growth "
            "and review high-value vendors."
        )

    else:

        positive_signals.append(
            {
                "title": "Controlled Expenses",
                "description": (
                    f"Expenses represent "
                    f"{expense_ratio:.1f}% "
                    f"of income."
                ),
            }
        )

    # ---------------------------------------
    # Rule 3: Largest spending category
    # ---------------------------------------

    by_category = stats.get(
        "by_category"
    )

    if (
        by_category is not None
        and len(by_category) > 0
    ):

        largest_category = (
            by_category.index[0]
        )

        largest_amount = _safe_float(
            by_category.iloc[0]
        )

        opportunities.append(
            {
                "title": "Review Largest Cost Area",
                "description": (
                    f"{largest_category} is the "
                    f"largest spending category at "
                    f"${largest_amount:,.2f}."
                ),
            }
        )

        recommendations.append(
            f"Review {largest_category} spending "
            "for possible savings or efficiency gains."
        )

        findings.append(
            {
                "type": "Opportunity",
                "title": "Largest Cost Area",
                "description": (
                    f"{largest_category}: "
                    f"${largest_amount:,.2f}"
                ),
            }
        )

    # ---------------------------------------
    # Rule 4: Highest vendor
    # ---------------------------------------

    top_vendors = stats.get(
        "top_vendors"
    )

    if (
        top_vendors is not None
        and len(top_vendors) > 0
    ):

        top_vendor = top_vendors.index[0]

        top_vendor_amount = _safe_float(
            top_vendors.iloc[0]
        )

        findings.append(
            {
                "type": "Vendor",
                "title": "Highest-Spend Vendor",
                "description": (
                    f"{top_vendor} accounts for "
                    f"${top_vendor_amount:,.2f} "
                    "of spending."
                ),
            }
        )

        opportunities.append(
            {
                "title": "Vendor Optimization",
                "description": (
                    f"{top_vendor} is the highest "
                    f"spend at "
                    f"${top_vendor_amount:,.2f}."
                ),
            }
        )

    # ---------------------------------------
    # Rule 5: Recurring expenses
    # ---------------------------------------

    recurring = stats.get(
        "recurring"
    )

    if (
        recurring is not None
        and len(recurring) > 0
    ):

        recurring_count = len(
            recurring
        )

        opportunities.append(
            {
                "title": "Recurring Cost Review",
                "description": (
                    f"{recurring_count} recurring "
                    "expenses were detected."
                ),
            }
        )

        recommendations.append(
            "Review recurring subscriptions, "
            "services and vendor contracts for "
            "unused or duplicate costs."
        )

        findings.append(
            {
                "type": "Pattern",
                "title": "Recurring Expenses",
                "description": (
                    f"{recurring_count} recurring "
                    "expense patterns detected."
                ),
            }
        )

    # ---------------------------------------
    # Rule 6: Transaction volume
    # ---------------------------------------

    transaction_count = len(df)

    findings.append(
        {
            "type": "Data",
            "title": "Transactions Analyzed",
            "description": (
                f"{transaction_count} financial "
                "transactions processed."
            ),
        }
    )

    # ---------------------------------------
    # Ensure recommendations exist
    # ---------------------------------------

    if not recommendations:

        recommendations.append(
            "Continue monitoring monthly cash flow "
            "and major spending categories."
        )

    return {
        "health_score": health_score,
        "status": status,
        "risks": risks,
        "opportunities": opportunities,
        "recommendations": recommendations,
        "positive_signals": positive_signals,
        "findings": findings,
        "transaction_count": transaction_count,
        "net_cash_flow": net_cash_flow,
        "expense_ratio": expense_ratio,
    }