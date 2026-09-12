"""
Centralized financial state for FinTrack AI.
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

import pandas as pd


AGENT_ORDER: List[str] = [
    "Data Agent",
    "Categorization Agent",
    "Analytics Agent",
    "Risk Agent",
    "Opportunity Agent",
    "Decision Agent",
    "Critic Agent",
    "Insight Agent",
]


def empty_agent_status() -> Dict[str, Dict[str, Any]]:
    return {
        name: {"status": "pending", "message": "", "detail": ""}
        for name in AGENT_ORDER
    }


@dataclass
class FinancialState:
    df: Optional[pd.DataFrame] = None
    quality: Dict[str, Any] = field(default_factory=dict)
    stats: Dict[str, Any] = field(default_factory=dict)
    risk: Dict[str, Any] = field(default_factory=dict)
    opportunity: Dict[str, Any] = field(default_factory=dict)
    decision: Dict[str, Any] = field(default_factory=dict)
    critic: Dict[str, Any] = field(default_factory=dict)
    summary: Dict[str, Any] = field(default_factory=dict)
    agent_status: Dict[str, Dict[str, Any]] = field(default_factory=empty_agent_status)
    revision_count: int = 0
    errors: List[str] = field(default_factory=list)

    def set_status(self, agent: str, status: str, message: str = "", detail: str = "") -> None:
        if agent not in self.agent_status:
            self.agent_status[agent] = {"status": "pending", "message": "", "detail": ""}
        self.agent_status[agent]["status"] = status
        self.agent_status[agent]["message"] = message
        self.agent_status[agent]["detail"] = detail

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["df"] = None
        return data

    def is_complete(self) -> bool:
        return (
            self.df is not None
            and not self.df.empty
            and bool(self.decision)
            and bool(self.summary)
        )

    def financial_health_score(self) -> int:
        if not self.stats or not self.risk:
            return 0
        score = 100.0

        net = self.stats.get("net_cash_flow", 0.0)
        revenue = self.stats.get("total_revenue", 0.0)
        expense_ratio = self.stats.get("expense_ratio", 0.0)
        risk_score = self.risk.get("risk_score", 50)

        if net < 0:
            score -= 30
        elif revenue > 0:
            margin = net / revenue
            if margin < 0.1:
                score -= 15
            elif margin < 0.25:
                score -= 8

        if expense_ratio > 90:
            score -= 25
        elif expense_ratio > 75:
            score -= 15
        elif expense_ratio > 60:
            score -= 8

        score -= risk_score * 0.35

        return int(max(0, min(100, round(score))))

    def health_label(self) -> str:
        s = self.financial_health_score()
        if s >= 80:
            return "Healthy"
        if s >= 60:
            return "Stable"
        if s >= 40:
            return "Watch"
        return "At Risk"


# =====================================================================
# Convenience accessors used by every page
# =====================================================================
def get_financial_state() -> FinancialState:
    import streamlit as st

    if "fin_state" not in st.session_state:
        st.session_state.fin_state = FinancialState()
    return st.session_state.fin_state


def reset_financial_state() -> FinancialState:
    import streamlit as st

    st.session_state.fin_state = FinancialState()
    return st.session_state.fin_state
