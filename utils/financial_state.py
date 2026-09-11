"""
Shared financial analysis state for FinTrack AI.

Central pipeline:

    Raw Data
        ↓
    Data Agent
        ↓
    Categorization Agent
        ↓
    Analytics Agent
        ↓
    ┌───────────────┐
    ↓               ↓
 Risk Agent   Opportunity Agent
    └───────┬───────┘
            ↓
      Decision Agent
            ↓
       Critic Agent
            ↓
       Insight Agent

The resulting state is stored in Streamlit session state
so every page can use the same analysis.
"""

import hashlib
import os
from typing import Any

import pandas as pd
import streamlit as st

from agents.categorize import categorize_transactions
from agents.insights import generate_summary
from agents.strategic_agents import (
    run_strategic_agents,
)
from utils.data_processing import (
    compute_stats,
    load_and_clean,
)


# ============================================================
# SOURCE ID
# ============================================================

def _get_source_id(file) -> str:
    """Create a stable ID for the analyzed data source."""

    if isinstance(file, str):
        return file

    try:
        current_position = file.tell()

        file.seek(0)
        content = file.read()

        file.seek(current_position)

        return hashlib.md5(
            content
        ).hexdigest()

    except Exception:
        return str(file)


# ============================================================
# MAIN ANALYSIS PIPELINE
# ============================================================

def run_financial_analysis(
    file,
    use_llm: bool = True,
) -> dict[str, Any]:
    """
    Run the complete FinTrack AI agentic pipeline.

    Returns one shared state dictionary containing:

        df
        stats
        risk
        opportunity
        decision
        critic
        decisions
        summary
        agent_status
    """

    agent_status = {}

    # ========================================================
    # 1. DATA AGENT
    # ========================================================

    df = load_and_clean(file)

    agent_status["Data Agent"] = {
        "status": "complete",
        "message": (
            f"{len(df)} transactions cleaned"
        ),
        "count": len(df),
    }

    # ========================================================
    # 2. CATEGORIZATION AGENT
    # ========================================================

    df = categorize_transactions(
        df,
        use_llm=use_llm,
    )

    agent_status["Categorization Agent"] = {
        "status": "complete",
        "message": (
            f"{len(df)} transactions classified"
        ),
        "count": len(df),
    }

    # ========================================================
    # 3. ANALYTICS AGENT
    # ========================================================

    stats = compute_stats(df)

    pattern_count = 0

    by_category = stats.get(
        "by_category"
    )

    if by_category is not None:
        pattern_count += len(
            by_category
        )

    recurring = stats.get(
        "recurring"
    )

    if recurring is not None:
        pattern_count += len(
            recurring
        )

    agent_status["Analytics Agent"] = {
        "status": "complete",
        "message": (
            f"{pattern_count} financial patterns analyzed"
        ),
        "count": pattern_count,
    }

    # ========================================================
    # 4. STRATEGIC AGENTS
    # ========================================================

    strategic = run_strategic_agents(
        df,
        stats,
    )

    risk_result = strategic[
        "risk"
    ]

    opportunity_result = strategic[
        "opportunity"
    ]

    decision_result = strategic[
        "decision"
    ]

    critic_result = strategic[
        "critic"
    ]

    # --------------------------------------------------------
    # RISK AGENT
    # --------------------------------------------------------

    risk_count = len(
        risk_result.get(
            "risks",
            [],
        )
    )

    agent_status["Risk Agent"] = {
        "status": "complete",
        "message": (
            f"{risk_count} risks detected"
        ),
        "count": risk_count,
        "risk_level": risk_result.get(
            "risk_level",
            "Low",
        ),
    }

    # --------------------------------------------------------
    # OPPORTUNITY AGENT
    # --------------------------------------------------------

    opportunity_count = len(
        opportunity_result.get(
            "opportunities",
            [],
        )
    )

    agent_status["Opportunity Agent"] = {
        "status": "complete",
        "message": (
            f"{opportunity_count} opportunities identified"
        ),
        "count": opportunity_count,
    }

    # --------------------------------------------------------
    # DECISION AGENT
    # --------------------------------------------------------

    strategic_decision = decision_result.get(
        "decision",
        {},
    )

    agent_status["Decision Agent"] = {
        "status": "complete",
        "message": (
            strategic_decision.get(
                "title",
                "Decision generated",
            )
        ),
        "decision": strategic_decision,
    }

    # --------------------------------------------------------
    # CRITIC AGENT
    # --------------------------------------------------------

    critic_approved = critic_result.get(
        "approved",
        False,
    )

    agent_status["Critic Agent"] = {
        "status": (
            "complete"
            if critic_approved
            else "review"
        ),
        "message": (
            "Decision verified"
            if critic_approved
            else "Decision requires revision"
        ),
        "verdict": critic_result.get(
            "verdict",
            "REVISE",
        ),
    }

    # ========================================================
    # 5. COMPATIBILITY DECISION OBJECT
    # ========================================================
    #
    # Existing pages currently expect:
    #
    # decisions["health_score"]
    # decisions["status"]
    # decisions["risks"]
    # decisions["opportunities"]
    # decisions["recommendations"]
    # decisions["positive_signals"]
    # decisions["findings"]
    #
    # Keep that interface while adding the new agent outputs.
    # ========================================================

    income = float(
        stats.get(
            "total_income",
            0,
        )
    )

    expenses = float(
        stats.get(
            "total_expense",
            0,
        )
    )

    net_cash_flow = (
        income - expenses
    )

    if income > 0:
        expense_ratio = (
            expenses / income
        ) * 100
    else:
        expense_ratio = 100.0

    # --------------------------------------------------------
    # HEALTH SCORE
    # --------------------------------------------------------

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

        health_status = "Healthy"

    elif health_score >= 60:

        health_status = "Moderate Risk"

    else:

        health_status = "High Risk"

    # --------------------------------------------------------
    # RISKS
    # --------------------------------------------------------

    risks = []

    for risk in risk_result.get(
        "risks",
        [],
    ):

        risks.append(
            {
                "title": risk.get(
                    "title",
                    "Financial Risk",
                ),
                "description": risk.get(
                    "description",
                    "",
                ),
                "severity": risk.get(
                    "severity",
                    "Medium",
                ),
            }
        )

    # --------------------------------------------------------
    # OPPORTUNITIES
    # --------------------------------------------------------

    opportunities = []

    for opportunity in opportunity_result.get(
        "opportunities",
        [],
    ):

        opportunities.append(
            {
                "title": opportunity.get(
                    "title",
                    "Financial Opportunity",
                ),
                "description": opportunity.get(
                    "description",
                    "",
                ),
                "priority": opportunity.get(
                    "priority",
                    "Medium",
                ),
            }
        )

    # --------------------------------------------------------
    # RECOMMENDATIONS
    # --------------------------------------------------------

    recommendations = []

    for opportunity in opportunities:

        description = opportunity.get(
            "description",
            "",
        )

        if description:
            recommendations.append(
                description
            )

    for risk in risks:

        description = risk.get(
            "description",
            "",
        )

        if description:
            recommendations.append(
                description
            )

    if not recommendations:

        recommendations.append(
            "Continue monitoring monthly cash flow "
            "and major spending categories."
        )

    # --------------------------------------------------------
    # POSITIVE SIGNALS
    # --------------------------------------------------------

    positive_signals = []

    if net_cash_flow > 0:

        positive_signals.append(
            {
                "title": "Positive Cash Flow",
                "description": (
                    f"Income exceeds expenses by "
                    f"${net_cash_flow:,.2f}."
                ),
            }
        )

    if expense_ratio <= 65:

        positive_signals.append(
            {
                "title": "Controlled Expenses",
                "description": (
                    f"Expenses represent "
                    f"{expense_ratio:.1f}% "
                    "of income."
                ),
            }
        )

    # --------------------------------------------------------
    # FINDINGS
    # --------------------------------------------------------

    findings = []

    for risk in risks:

        findings.append(
            {
                "type": "Risk",
                "title": risk["title"],
                "description": risk["description"],
            }
        )

    for opportunity in opportunities:

        findings.append(
            {
                "type": "Opportunity",
                "title": opportunity["title"],
                "description": opportunity["description"],
            }
        )

    if net_cash_flow > 0:

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

    findings.append(
        {
            "type": "Data",
            "title": "Transactions Analyzed",
            "description": (
                f"{len(df)} financial transactions "
                "processed."
            ),
        }
    )

    # ========================================================
    # FINAL COMPATIBLE DECISION OBJECT
    # ========================================================

    decisions = {
        "health_score": health_score,
        "status": health_status,
        "risks": risks,
        "opportunities": opportunities,
        "recommendations": recommendations,
        "positive_signals": positive_signals,
        "findings": findings,
        "transaction_count": len(df),
        "net_cash_flow": net_cash_flow,
        "expense_ratio": expense_ratio,

        # New agentic outputs
        "risk_agent": risk_result,
        "opportunity_agent": opportunity_result,
        "strategic_decision": decision_result,
        "critic_agent": critic_result,
    }

    # ========================================================
    # 6. INSIGHT AGENT
    # ========================================================

    try:

        summary = generate_summary(
            stats,
            decisions,
        )

        insight_status = "complete"

        insight_message = (
            "Financial briefing generated"
        )

    except Exception as exc:

        summary = (
            "Financial analysis completed. "
            "Review the detected risks, opportunities "
            "and recommended actions."
        )

        insight_status = "fallback"

        insight_message = (
            "Fallback briefing generated"
        )

        print(
            "[financial_state] "
            f"Insight Agent failed: {exc}"
        )

    agent_status["Insight Agent"] = {
        "status": insight_status,
        "message": insight_message,
    }

    # ========================================================
    # COMPLETE SHARED STATE
    # ========================================================

    return {
        # Core data
        "df": df,
        "stats": stats,

        # Agentic outputs
        "risk": risk_result,
        "opportunity": opportunity_result,
        "decision": decision_result,
        "critic": critic_result,

        # Backward-compatible decision object
        "decisions": decisions,

        # Insight
        "summary": summary,

        # Agent execution state
        "agent_status": agent_status,

        # Source information
        "source_id": _get_source_id(file),

        "llm_enabled": bool(
            use_llm
            and os.environ.get(
                "HF_TOKEN"
            )
        ),
    }


# ============================================================
# STREAMLIT STATE HELPERS
# ============================================================

def save_financial_state(
    state: dict[str, Any],
) -> None:
    """Save analysis results into Streamlit session state."""

    st.session_state[
        "financial_state"
    ] = state


def get_financial_state() -> dict[str, Any] | None:
    """Retrieve the current financial analysis state."""

    return st.session_state.get(
        "financial_state"
    )


def clear_financial_state() -> None:
    """Clear the current analysis state."""

    if "financial_state" in st.session_state:

        del st.session_state[
            "financial_state"
        ]


def has_financial_state() -> bool:
    """Return True when analysis has been completed."""

    return (
        "financial_state"
        in st.session_state
    )


def get_financial_dataframe():
    """Return the analyzed dataframe."""

    state = get_financial_state()

    if not state:
        return None

    return state.get("df")


def get_financial_stats():
    """Return financial statistics."""

    state = get_financial_state()

    if not state:
        return None

    return state.get("stats")


def get_decisions():
    """Return the compatible decision object."""

    state = get_financial_state()

    if not state:
        return None

    return state.get("decisions")


def get_risk_agent():
    """Return Risk Agent output."""

    state = get_financial_state()

    if not state:
        return None

    return state.get("risk")


def get_opportunity_agent():
    """Return Opportunity Agent output."""

    state = get_financial_state()

    if not state:
        return None

    return state.get("opportunity")


def get_strategic_decision():
    """Return Strategic Decision Agent output."""

    state = get_financial_state()

    if not state:
        return None

    return state.get("decision")


def get_critic_agent():
    """Return Critic Agent output."""

    state = get_financial_state()

    if not state:
        return None

    return state.get("critic")


def get_agent_status() -> dict:
    """Return status information for all agents."""

    state = get_financial_state()

    if not state:
        return {}

    return state.get(
        "agent_status",
        {},
    )