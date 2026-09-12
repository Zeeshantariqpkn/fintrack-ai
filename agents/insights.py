"""
Insight Agent — executive financial briefing.
"""
from __future__ import annotations

import json
from typing import Any, Dict

from agents.strategic_agents import call_hf, hf_available


def _deterministic_summary(
    stats: Dict[str, Any],
    risk: Dict[str, Any],
    opportunity: Dict[str, Any],
    decision: Dict[str, Any],
    critic: Dict[str, Any],
    health_score: int,
    health_label: str,
) -> Dict[str, Any]:
    revenue = stats.get("total_revenue", 0.0)
    expenses = stats.get("total_expenses", 0.0)
    net = stats.get("net_cash_flow", 0.0)
    er = stats.get("expense_ratio", 0.0)

    cash_flow_line = (
        f"Revenue remains {'significantly above' if net > 0 else 'below'} total "
        f"expenses, resulting in {'positive' if net > 0 else 'negative'} cash flow "
        f"of ${net:,.0f}."
    )

    if opportunity.get("opportunities"):
        top_opp = opportunity["opportunities"][0]
        opp_line = f"The largest optimization opportunity is {top_opp['title']}: {top_opp['description']}"
    else:
        opp_line = "No major optimization opportunities were detected."

    next_step = decision.get("recommended_actions", ["Continue monitoring."])[0]

    narrative = (
        f"Financial Health: {health_score}/100 — {health_label}\n\n"
        f"{cash_flow_line}\n\n"
        f"{opp_line}\n\n"
        f"Recommended next step: {next_step}"
    )

    return {
        "health_score": health_score,
        "health_label": health_label,
        "headline": f"{health_label} financial position with a net cash flow of ${net:,.0f}.",
        "narrative": narrative,
        "method": "deterministic",
    }


def run_insight_agent(
    stats: Dict[str, Any],
    risk: Dict[str, Any],
    opportunity: Dict[str, Any],
    decision: Dict[str, Any],
    critic: Dict[str, Any],
    health_score: int,
    health_label: str,
    use_ai: bool = True,
) -> Dict[str, Any]:
    fallback = _deterministic_summary(
        stats, risk, opportunity, decision, critic, health_score, health_label
    )

    if not (use_ai and hf_available()):
        return fallback

    prompt = (
        "You are the Insight Agent in a financial analytics system. Write a concise "
        "executive briefing (max 150 words) using ONLY the data provided. Include the "
        "financial health score, cash-flow status, the top opportunity, and the "
        "recommended next step. Do not invent numbers.\n\n"
        f"Health: {health_score}/100 ({health_label})\n"
        f"Analytics: {json.dumps({k: v for k, v in stats.items() if k != 'monthly'})[:1800]}\n"
        f"Risk: {json.dumps(risk)[:1000]}\n"
        f"Opportunity: {json.dumps(opportunity)[:1000]}\n"
        f"Decision: {json.dumps(decision)[:1000]}\n"
        f"Critic: {json.dumps(critic)[:600]}\n\n"
        "Briefing:"
    )
    text = call_hf(prompt, max_new_tokens=300, temperature=0.4)
    if not text:
        return fallback

    return {
        "health_score": health_score,
        "health_label": health_label,
        "headline": fallback["headline"],
        "narrative": text.strip(),
        "method": "ai",
    }
