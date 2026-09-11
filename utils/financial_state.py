"""
Shared financial analysis state for FinTrack AI.

This module provides one central analysis pipeline that can be
used by the Overview and all Streamlit pages.
"""

import hashlib
import os
from typing import Any

import pandas as pd
import streamlit as st

from agents.categorize import categorize_transactions
from agents.decision import run_decision_agent
from agents.insights import generate_summary
from utils.data_processing import compute_stats, load_and_clean


def _get_source_id(file) -> str:
    """Create a stable ID for the uploaded/sample data."""

    if isinstance(file, str):
        return file

    try:
        current_position = file.tell()
        file.seek(0)
        content = file.read()
        file.seek(current_position)

        return hashlib.md5(content).hexdigest()

    except Exception:
        return str(file)


def run_financial_analysis(
    file,
    use_llm: bool = True,
) -> dict[str, Any]:
    """
    Run the complete FinTrack AI analysis pipeline.

    Pipeline:

        Raw Data
            ↓
        Data Agent
            ↓
        Categorization Agent
            ↓
        Analytics Agent
            ↓
        Decision Agent
            ↓
        Insight Agent

    Returns a shared financial state dictionary.
    """

    agent_status = {}

    # ---------------------------------------------------------
    # 1. DATA AGENT
    # ---------------------------------------------------------

    df = load_and_clean(file)

    agent_status["Data Agent"] = {
        "status": "complete",
        "message": f"{len(df)} transactions cleaned",
        "count": len(df),
    }

    # ---------------------------------------------------------
    # 2. CATEGORIZATION AGENT
    # ---------------------------------------------------------

    df = categorize_transactions(
        df,
        use_llm=use_llm,
    )

    agent_status["Categorization Agent"] = {
        "status": "complete",
        "message": f"{len(df)} transactions classified",
        "count": len(df),
    }

    # ---------------------------------------------------------
    # 3. ANALYTICS AGENT
    # ---------------------------------------------------------

    stats = compute_stats(df)

    pattern_count = 0

    if stats.get("by_category") is not None:
        pattern_count += len(stats["by_category"])

    if stats.get("recurring") is not None:
        pattern_count += len(stats["recurring"])

    agent_status["Analytics Agent"] = {
        "status": "complete",
        "message": f"{pattern_count} financial patterns analyzed",
        "count": pattern_count,
    }

    # ---------------------------------------------------------
    # 4. DECISION AGENT
    # ---------------------------------------------------------

    decisions = run_decision_agent(
        df,
        stats,
    )

    risk_count = len(
        decisions.get("risks", [])
    )

    opportunity_count = len(
        decisions.get("opportunities", [])
    )

    agent_status["Decision Agent"] = {
        "status": "complete",
        "message": (
            f"{risk_count} risks, "
            f"{opportunity_count} opportunities"
        ),
        "risks": risk_count,
        "opportunities": opportunity_count,
    }

    # ---------------------------------------------------------
    # 5. INSIGHT AGENT
    # ---------------------------------------------------------

    try:
        summary = generate_summary(
            stats,
            decisions,
        )

        insight_status = "complete"
        insight_message = "Financial briefing generated"

    except Exception as exc:
        summary = (
            "Financial analysis completed. "
            "Review the detected risks, opportunities "
            "and recommendations."
        )

        insight_status = "fallback"
        insight_message = "Fallback briefing generated"

        print(
            f"[financial_state] Insight Agent failed: {exc}"
        )

    agent_status["Insight Agent"] = {
        "status": insight_status,
        "message": insight_message,
    }

    # ---------------------------------------------------------
    # SHARED STATE
    # ---------------------------------------------------------

    return {
        "df": df,
        "stats": stats,
        "decisions": decisions,
        "summary": summary,
        "agent_status": agent_status,
        "source_id": _get_source_id(file),
        "llm_enabled": bool(
            use_llm and os.environ.get("HF_TOKEN")
        ),
    }


def save_financial_state(
    state: dict[str, Any],
) -> None:
    """
    Save the analysis state into Streamlit session state.
    """

    st.session_state["financial_state"] = state


def get_financial_state() -> dict[str, Any] | None:
    """
    Retrieve the current financial analysis state.
    """

    return st.session_state.get(
        "financial_state"
    )


def clear_financial_state() -> None:
    """
    Clear the current analysis state.
    """

    if "financial_state" in st.session_state:
        del st.session_state["financial_state"]


def has_financial_state() -> bool:
    """
    Check whether financial analysis has been completed.
    """

    return (
        "financial_state"
        in st.session_state
    )


def get_financial_dataframe() -> pd.DataFrame | None:
    """
    Return the analyzed transaction dataframe.
    """

    state = get_financial_state()

    if not state:
        return None

    return state.get("df")


def get_financial_stats() -> dict | None:
    """
    Return calculated financial statistics.
    """

    state = get_financial_state()

    if not state:
        return None

    return state.get("stats")


def get_decisions() -> dict | None:
    """
    Return Decision Agent results.
    """

    state = get_financial_state()

    if not state:
        return None

    return state.get("decisions")


def get_agent_status() -> dict:
    """
    Return status information for all agents.
    """

    state = get_financial_state()

    if not state:
        return {}

    return state.get(
        "agent_status",
        {},
    )