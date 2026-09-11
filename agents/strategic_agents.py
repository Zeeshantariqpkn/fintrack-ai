"""
Strategic agents for FinTrack AI.

Contains:
- Risk Agent
- Opportunity Agent
- Decision Agent
- Critic / Review Agent

These agents operate on shared financial evidence and
produce structured outputs that can be passed between agents.
"""

from typing import Any

import pandas as pd


# ============================================================
# HELPERS
# ============================================================

def _safe_float(value: Any) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def _evidence(
    metric: str,
    value: Any,
    interpretation: str,
) -> dict:
    return {
        "metric": metric,
        "value": value,
        "interpretation": interpretation,
    }


# ============================================================
# RISK AGENT
# ============================================================

def run_risk_agent(
    df: pd.DataFrame,
    stats: dict,
) -> dict:
    """
    Analyze financial evidence specifically for risks.

    The Risk Agent does not decide the final business action.
    It only identifies and prioritizes financial threats.
    """

    risks = []
    evidence = []

    income = _safe_float(
        stats.get("total_income", 0)
    )

    expenses = _safe_float(
        stats.get("total_expense", 0)
    )

    net_cash_flow = income - expenses

    expense_ratio = (
        (expenses / income) * 100
        if income > 0
        else 100.0
    )

    # --------------------------------------------------------
    # CASH FLOW RISK
    # --------------------------------------------------------

    if net_cash_flow < 0:

        risks.append(
            {
                "title": "Negative Cash Flow",
                "severity": "High",
                "description": (
                    f"Expenses exceed income by "
                    f"${abs(net_cash_flow):,.2f}."
                ),
            }
        )

        evidence.append(
            _evidence(
                "Net cash flow",
                f"${net_cash_flow:,.2f}",
                "Outgoing cash exceeds incoming cash.",
            )
        )

    # --------------------------------------------------------
    # EXPENSE RATIO RISK
    # --------------------------------------------------------

    if expense_ratio > 80:

        risks.append(
            {
                "title": "High Expense Burden",
                "severity": "High",
                "description": (
                    f"Expenses consume "
                    f"{expense_ratio:.1f}% of revenue."
                ),
            }
        )

        evidence.append(
            _evidence(
                "Expense ratio",
                f"{expense_ratio:.1f}%",
                "Very high proportion of revenue is consumed by expenses.",
            )
        )

    elif expense_ratio > 65:

        risks.append(
            {
                "title": "Cost Pressure",
                "severity": "Medium",
                "description": (
                    f"Expenses consume "
                    f"{expense_ratio:.1f}% of revenue."
                ),
            }
        )

        evidence.append(
            _evidence(
                "Expense ratio",
                f"{expense_ratio:.1f}%",
                "Expenses are taking a significant share of revenue.",
            )
        )

    # --------------------------------------------------------
    # CONCENTRATION RISK
    # --------------------------------------------------------

    by_category = stats.get(
        "by_category"
    )

    if (
        by_category is not None
        and len(by_category) > 0
        and expenses > 0
    ):

        largest_category = by_category.index[0]

        largest_amount = _safe_float(
            by_category.iloc[0]
        )

        concentration = (
            largest_amount / expenses
        ) * 100

        if concentration > 40:

            risks.append(
                {
                    "title": "Expense Concentration",
                    "severity": "Medium",
                    "description": (
                        f"{largest_category} represents "
                        f"{concentration:.1f}% of total expenses."
                    ),
                }
            )

            evidence.append(
                _evidence(
                    "Largest expense category",
                    (
                        f"{largest_category}: "
                        f"${largest_amount:,.2f}"
                    ),
                    (
                        f"{concentration:.1f}% of expenses "
                        "are concentrated in one category."
                    ),
                )
            )

    # --------------------------------------------------------
    # RECURRING EXPENSE RISK
    # --------------------------------------------------------

    recurring = stats.get(
        "recurring"
    )

    if (
        recurring is not None
        and len(recurring) >= 5
    ):

        risks.append(
            {
                "title": "Recurring Cost Exposure",
                "severity": "Low",
                "description": (
                    f"{len(recurring)} recurring expense "
                    "patterns were detected."
                ),
            }
        )

        evidence.append(
            _evidence(
                "Recurring expenses",
                len(recurring),
                "Multiple recurring costs may require periodic review.",
            )
        )

    # --------------------------------------------------------
    # RISK SCORE
    # --------------------------------------------------------

    severity_points = {
        "High": 30,
        "Medium": 20,
        "Low": 10,
    }

    risk_score = sum(
        severity_points.get(
            risk.get("severity"),
            0,
        )
        for risk in risks
    )

    risk_score = min(
        risk_score,
        100,
    )

    if risk_score >= 60:
        level = "High"
    elif risk_score >= 30:
        level = "Moderate"
    else:
        level = "Low"

    return {
        "agent": "Risk Agent",
        "risk_score": risk_score,
        "risk_level": level,
        "risks": risks,
        "evidence": evidence,
        "reasoning": (
            "The Risk Agent evaluated cash flow, "
            "expense burden, concentration and "
            "recurring spending patterns."
        ),
    }


# ============================================================
# OPPORTUNITY AGENT
# ============================================================

def run_opportunity_agent(
    df: pd.DataFrame,
    stats: dict,
    risk_result: dict | None = None,
) -> dict:
    """
    Search for financial improvement opportunities.

    The Opportunity Agent looks for areas where the business
    can reduce costs, improve efficiency or strengthen cash flow.
    """

    opportunities = []
    evidence = []

    income = _safe_float(
        stats.get("total_income", 0)
    )

    expenses = _safe_float(
        stats.get("total_expense", 0)
    )

    # --------------------------------------------------------
    # LARGEST COST AREA
    # --------------------------------------------------------

    by_category = stats.get(
        "by_category"
    )

    if (
        by_category is not None
        and len(by_category) > 0
    ):

        category = by_category.index[0]

        amount = _safe_float(
            by_category.iloc[0]
        )

        opportunities.append(
            {
                "title": "Optimize Largest Cost Area",
                "priority": "High",
                "description": (
                    f"{category} is the largest "
                    f"expense category at "
                    f"${amount:,.2f}."
                ),
            }
        )

        evidence.append(
            _evidence(
                "Largest cost category",
                f"{category}: ${amount:,.2f}",
                "This category provides the largest visible cost-optimization target.",
            )
        )

    # --------------------------------------------------------
    # VENDOR OPTIMIZATION
    # --------------------------------------------------------

    top_vendors = stats.get(
        "top_vendors"
    )

    if (
        top_vendors is not None
        and len(top_vendors) > 0
    ):

        vendor = top_vendors.index[0]

        amount = _safe_float(
            top_vendors.iloc[0]
        )

        opportunities.append(
            {
                "title": "Review Top Vendor",
                "priority": "Medium",
                "description": (
                    f"{vendor} is the highest-spend "
                    f"vendor at ${amount:,.2f}."
                ),
            }
        )

        evidence.append(
            _evidence(
                "Highest-spend vendor",
                f"{vendor}: ${amount:,.2f}",
                "Vendor negotiation or alternative sourcing may reduce costs.",
            )
        )

    # --------------------------------------------------------
    # RECURRING COST OPTIMIZATION
    # --------------------------------------------------------

    recurring = stats.get(
        "recurring"
    )

    if (
        recurring is not None
        and len(recurring) > 0
    ):

        opportunities.append(
            {
                "title": "Audit Recurring Expenses",
                "priority": "Medium",
                "description": (
                    f"{len(recurring)} recurring "
                    "expenses can be reviewed for "
                    "unused services or duplicate costs."
                ),
            }
        )

        evidence.append(
            _evidence(
                "Recurring expense patterns",
                len(recurring),
                "Recurring services should be periodically reviewed.",
            )
        )

    # --------------------------------------------------------
    # POSITIVE CASH FLOW OPPORTUNITY
    # --------------------------------------------------------

    net_cash_flow = income - expenses

    if net_cash_flow > 0:

        opportunities.append(
            {
                "title": "Strengthen Cash Position",
                "priority": "Medium",
                "description": (
                    f"The business generated "
                    f"${net_cash_flow:,.2f} "
                    "of positive net cash flow."
                ),
            }
        )

        evidence.append(
            _evidence(
                "Net cash flow",
                f"${net_cash_flow:,.2f}",
                "Positive cash generation creates room for strategic planning.",
            )
        )

    return {
        "agent": "Opportunity Agent",
        "opportunity_count": len(
            opportunities
        ),
        "opportunities": opportunities,
        "evidence": evidence,
        "reasoning": (
            "The Opportunity Agent searched for "
            "cost optimization, vendor improvements, "
            "recurring-cost savings and cash-flow opportunities."
        ),
    }


# ============================================================
# DECISION AGENT
# ============================================================

def run_strategic_decision_agent(
    risk_result: dict,
    opportunity_result: dict,
) -> dict:
    """
    Make a business decision using outputs from
    independent Risk and Opportunity agents.
    """

    risks = risk_result.get(
        "risks",
        []
    )

    opportunities = opportunity_result.get(
        "opportunities",
        []
    )

    risk_score = _safe_float(
        risk_result.get(
            "risk_score",
            0,
        )
    )

    # --------------------------------------------------------
    # PRIORITIZE HIGH-SEVERITY RISKS
    # --------------------------------------------------------

    high_risks = [
        risk
        for risk in risks
        if risk.get("severity") == "High"
    ]

    if high_risks:

        selected = high_risks[0]

        decision = {
            "title": selected.get(
                "title",
                "Address Financial Risk",
            ),
            "type": "Risk Mitigation",
            "priority": "Critical",
            "reason": selected.get(
                "description",
                "",
            ),
        }

    elif opportunities:

        selected = opportunities[0]

        decision = {
            "title": selected.get(
                "title",
                "Optimize Financial Performance",
            ),
            "type": "Opportunity",
            "priority": selected.get(
                "priority",
                "Medium",
            ),
            "reason": selected.get(
                "description",
                "",
            ),
        }

    else:

        decision = {
            "title": "Continue Financial Monitoring",
            "type": "Monitoring",
            "priority": "Low",
            "reason": (
                "No dominant financial risk or "
                "optimization opportunity was identified."
            ),
        }

    return {
        "agent": "Decision Agent",
        "decision": decision,
        "risk_score": risk_score,
        "considered_risks": len(risks),
        "considered_opportunities": len(
            opportunities
        ),
        "reasoning": (
            "The Decision Agent compared independent "
            "risk and opportunity outputs and selected "
            "the highest-priority business action."
        ),
    }


# ============================================================
# CRITIC / REVIEW AGENT
# ============================================================

def run_critic_agent(
    decision_result: dict,
    risk_result: dict,
    opportunity_result: dict,
) -> dict:
    """
    Review the proposed decision.

    The Critic Agent checks whether the decision is actually
    supported by the outputs of the other agents.
    """

    decision = decision_result.get(
        "decision",
        {},
    )

    title = decision.get(
        "title",
        "",
    )

    decision_reason = decision.get(
        "reason",
        "",
    )

    risks = risk_result.get(
        "risks",
        []
    )

    opportunities = opportunity_result.get(
        "opportunities",
        []
    )

    evidence = []

    supported = False

    # --------------------------------------------------------
    # CHECK RISK DECISION
    # --------------------------------------------------------

    if decision.get("type") == "Risk Mitigation":

        for risk in risks:

            if risk.get("title") == title:

                supported = True

                evidence.append(
                    {
                        "check": "Risk evidence",
                        "result": "PASS",
                        "details": (
                            f"Decision matches detected risk: "
                            f"{risk.get('description', '')}"
                        ),
                    }
                )

    # --------------------------------------------------------
    # CHECK OPPORTUNITY DECISION
    # --------------------------------------------------------

    elif decision.get("type") == "Opportunity":

        for opportunity in opportunities:

            if opportunity.get("title") == title:

                supported = True

                evidence.append(
                    {
                        "check": "Opportunity evidence",
                        "result": "PASS",
                        "details": (
                            f"Decision matches detected opportunity: "
                            f"{opportunity.get('description', '')}"
                        ),
                    }
                )

    # --------------------------------------------------------
    # FALLBACK MONITORING DECISION
    # --------------------------------------------------------

    else:

        if not risks and not opportunities:

            supported = True

            evidence.append(
                {
                    "check": "Evidence consistency",
                    "result": "PASS",
                    "details": (
                        "No dominant risk or opportunity "
                        "was detected."
                    ),
                }
            )

    # --------------------------------------------------------
    # FINAL REVIEW
    # --------------------------------------------------------

    if supported:

        verdict = "APPROVED"

        review = (
            "The proposed decision is supported by "
            "the outputs of the specialist agents."
        )

    else:

        verdict = "REVISE"

        review = (
            "The proposed decision could not be directly "
            "supported by the specialist-agent evidence."
        )

    return {
        "agent": "Critic Agent",
        "verdict": verdict,
        "approved": supported,
        "decision_reviewed": title,
        "decision_reason": decision_reason,
        "review": review,
        "evidence": evidence,
        "revision_required": not supported,
    }


# ============================================================
# COMPLETE STRATEGIC ANALYSIS
# ============================================================

def run_strategic_agents(
    df: pd.DataFrame,
    stats: dict,
) -> dict:
    """
    Run the complete strategic multi-agent layer.

    Flow:

        Analytics
             ↓
        ┌───────────────┐
        ↓               ↓
      Risk         Opportunity
        └───────┬───────┘
                ↓
             Decision
                ↓
              Critic
                ↓
          Approved/Revise
    """

    risk_result = run_risk_agent(
        df,
        stats,
    )

    opportunity_result = run_opportunity_agent(
        df,
        stats,
        risk_result,
    )

    decision_result = run_strategic_decision_agent(
        risk_result,
        opportunity_result,
    )

    critic_result = run_critic_agent(
        decision_result,
        risk_result,
        opportunity_result,
    )

    return {
        "risk": risk_result,
        "opportunity": opportunity_result,
        "decision": decision_result,
        "critic": critic_result,
    }