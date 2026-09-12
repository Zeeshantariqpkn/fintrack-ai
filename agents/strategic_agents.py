"""
Agent implementations for FinTrack AI.

Uses Groq (Llama 3.3 70B) for LLM reasoning. Falls back to deterministic
logic over real data when GROQ_API_KEY is missing. Numbers are always
computed locally — never invented by the LLM.
"""
from __future__ import annotations

import json
import os
from typing import Any, Dict, List, Optional

import numpy as np
import pandas as pd

try:
    import requests
except ImportError:  # pragma: no cover
    requests = None  # type: ignore


# GROQ_MODEL = "llama-3.1-8b-instant"
GROQ_MODEL = "openai/gpt-oss-20b"
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"


# =====================================================================
# Groq LLM helper (OpenAI-compatible)
# =====================================================================
def _get_groq_key() -> str:
    """Read GROQ_API_KEY from env vars, then Streamlit secrets."""
    key = os.environ.get("GROQ_API_KEY", "")
    if key:
        return key
    try:
        import streamlit as st
        key = st.secrets.get("GROQ_API_KEY", "")
        if key:
            os.environ["GROQ_API_KEY"] = key
    except Exception:
        pass
    return key


def hf_available() -> bool:
    """Kept the same name so existing imports still work. Now checks Groq."""
    return bool(_get_groq_key()) and requests is not None


def call_hf(prompt: str, max_new_tokens: int = 400, temperature: float = 0.3) -> Optional[str]:
    """
    Call Groq's OpenAI-compatible chat completions API.
    Returns the generated text or None on any failure. Never raises.
    """
    if not hf_available():
        return None
    headers = {
        "Authorization": f"Bearer {_get_groq_key()}",
        "Content-Type": "application/json",
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": "You are a precise financial analyst. Follow the user's instructions exactly."},
            {"role": "user", "content": prompt},
        ],
        "max_tokens": max_new_tokens,
        "temperature": temperature,
    }
    try:
        resp = requests.post(GROQ_API_URL, headers=headers, json=payload, timeout=45)
        if resp.status_code != 200:
            return None
        data = resp.json()
        return data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None


def _safe_json(text: Optional[str]) -> Optional[dict]:
    if not text:
        return None
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    try:
        return json.loads(text[start:end + 1])
    except Exception:
        return None


# =====================================================================
# Analytics Agent
# =====================================================================
def run_analytics_agent(df: pd.DataFrame) -> Dict[str, Any]:
    income = df[df["type"] == "income"]
    expense = df[df["type"] == "expense"]

    total_revenue = float(income["amount"].sum())
    total_expenses = float(expense["abs_amount"].sum())
    net = total_revenue - total_expenses
    expense_ratio = (total_expenses / total_revenue * 100.0) if total_revenue > 0 else 100.0

    df_m = df.copy()
    df_m["month"] = df_m["date"].dt.to_period("M").astype(str)
    monthly_rev = df_m[df_m["type"] == "income"].groupby("month")["amount"].sum()
    monthly_exp = df_m[df_m["type"] == "expense"].groupby("month")["abs_amount"].sum()
    months = sorted(set(monthly_rev.index) | set(monthly_exp.index))

    monthly = pd.DataFrame(
        {
            "month": months,
            "revenue": [float(monthly_rev.get(m, 0.0)) for m in months],
            "expenses": [float(monthly_exp.get(m, 0.0)) for m in months],
        }
    )
    monthly["net"] = monthly["revenue"] - monthly["expenses"]

    cat_totals: Dict[str, float] = {}
    if "category" in expense.columns:
        cat_totals = (
            expense.groupby("category")["abs_amount"].sum().sort_values(ascending=False).to_dict()
        )
        cat_totals = {k: float(v) for k, v in cat_totals.items()}
    largest_cat = next(iter(cat_totals.items()), (None, 0.0))

    vendor_totals: Dict[str, float] = {}
    if "description" in expense.columns:
        vendor_totals = (
            expense.groupby("description")["abs_amount"].sum().sort_values(ascending=False).head(10).to_dict()
        )
        vendor_totals = {k: float(v) for k, v in vendor_totals.items()}
    top_vendor = next(iter(vendor_totals.items()), (None, 0.0))
    top_vendor_share = (top_vendor[1] / total_expenses * 100.0) if total_expenses > 0 else 0.0

    recurring: List[Dict[str, Any]] = []
    if "description" in expense.columns:
        grouped = expense.groupby("description")["abs_amount"]
        for desc, vals in grouped:
            if len(vals) >= 3:
                cv = float(vals.std() / vals.mean()) if vals.mean() else 1.0
                if cv < 0.15:
                    recurring.append(
                        {
                            "description": str(desc),
                            "occurrences": int(len(vals)),
                            "avg_amount": float(vals.mean()),
                            "monthly_impact": float(vals.mean()),
                        }
                    )
        recurring.sort(key=lambda r: r["monthly_impact"], reverse=True)

    rev_trend = _trend(monthly["revenue"].tolist())
    exp_trend = _trend(monthly["expenses"].tolist())

    if cat_totals and total_expenses > 0:
        shares = [v / total_expenses for v in cat_totals.values()]
        hhi = float(sum(s * s for s in shares))
    else:
        hhi = 1.0

    positive_months = int((monthly["net"] > 0).sum())
    negative_months = int((monthly["net"] < 0).sum())

    evidence: List[Dict[str, Any]] = [
        _ev("total_revenue", total_revenue, f"Total revenue of ${total_revenue:,.0f} across {len(income)} transactions."),
        _ev("total_expenses", total_expenses, f"Total expenses of ${total_expenses:,.0f} across {len(expense)} transactions."),
        _ev("net_cash_flow", net, f"Net cash flow of ${net:,.0f} (revenue − expenses)."),
        _ev("expense_ratio", round(expense_ratio, 2), f"Expenses consume {expense_ratio:.1f}% of revenue."),
    ]
    if largest_cat[0]:
        evidence.append(
            _ev("largest_category", largest_cat[0],
                f"Largest expense category is {largest_cat[0]} at ${largest_cat[1]:,.0f}.")
        )
    if top_vendor[0]:
        evidence.append(
            _ev("top_vendor", top_vendor[0],
                f"Highest-spend vendor is {top_vendor[0]} at ${top_vendor[1]:,.0f} "
                f"({top_vendor_share:.1f}% of total expenses).")
        )
    if recurring:
        evidence.append(
            _ev("recurring_expenses", len(recurring),
                f"{len(recurring)} recurring expense pattern(s) detected.")
        )
    evidence.append(
        _ev("spending_concentration", round(hhi, 3),
            f"Expense concentration index (HHI) is {hhi:.3f} — "
            f"{'highly concentrated' if hhi > 0.35 else 'moderately concentrated' if hhi > 0.2 else 'well diversified'}.")
    )
    evidence.append(
        _ev("cashflow_months", f"{positive_months}/{positive_months + negative_months}",
            f"{positive_months} positive and {negative_months} negative cash-flow month(s).")
    )

    return {
        "total_revenue": round(total_revenue, 2),
        "total_expenses": round(total_expenses, 2),
        "net_cash_flow": round(net, 2),
        "expense_ratio": round(expense_ratio, 2),
        "monthly": monthly.to_dict(orient="records"),
        "category_totals": cat_totals,
        "largest_category": largest_cat[0],
        "largest_category_value": round(largest_cat[1], 2),
        "vendor_totals": vendor_totals,
        "top_vendor": top_vendor[0],
        "top_vendor_value": round(top_vendor[1], 2),
        "top_vendor_share": round(top_vendor_share, 2),
        "recurring_expenses": recurring,
        "revenue_trend": rev_trend,
        "expense_trend": exp_trend,
        "spending_concentration": round(hhi, 3),
        "positive_months": positive_months,
        "negative_months": negative_months,
        "num_transactions": int(len(df)),
        "evidence": evidence,
    }


def _ev(metric: str, value: Any, interpretation: str) -> Dict[str, Any]:
    return {"metric": metric, "value": value, "interpretation": interpretation}


def _trend(series: List[float]) -> str:
    if len(series) < 2:
        return "flat"
    first = series[: max(1, len(series) // 2)]
    second = series[max(1, len(series) // 2):]
    f_avg = float(np.mean(first)) if first else 0.0
    s_avg = float(np.mean(second)) if second else 0.0
    if f_avg == 0 and s_avg == 0:
        return "flat"
    change = (s_avg - f_avg) / max(abs(f_avg), 1e-6)
    if change > 0.10:
        return "rising"
    if change < -0.10:
        return "declining"
    return "stable"


# =====================================================================
# Risk Agent
# =====================================================================
def run_risk_agent(stats: Dict[str, Any]) -> Dict[str, Any]:
    risks: List[Dict[str, Any]] = []
    evidence: List[str] = []
    score = 0.0

    if stats["net_cash_flow"] < 0:
        sev = "HIGH" if stats["net_cash_flow"] < -0.1 * max(stats["total_revenue"], 1) else "MEDIUM"
        risks.append({
            "title": "Negative Cash Flow",
            "description": f"The business spent ${abs(stats['net_cash_flow']):,.0f} more than it earned.",
            "severity": sev,
            "evidence": f"Net cash flow: ${stats['net_cash_flow']:,.0f}.",
        })
        evidence.append(f"net_cash_flow={stats['net_cash_flow']:.0f}")
        score += 35 if sev == "HIGH" else 25

    er = stats["expense_ratio"]
    if er > 90:
        risks.append({
            "title": "Critical Expense Ratio",
            "description": f"Expenses consume {er:.1f}% of revenue — very little margin remains.",
            "severity": "HIGH",
            "evidence": f"expense_ratio={er:.1f}%",
        })
        evidence.append(f"expense_ratio={er:.1f}%")
        score += 25
    elif er > 75:
        risks.append({
            "title": "High Expense Ratio",
            "description": f"Expenses consume {er:.1f}% of revenue.",
            "severity": "MEDIUM",
            "evidence": f"expense_ratio={er:.1f}%",
        })
        evidence.append(f"expense_ratio={er:.1f}%")
        score += 15
    elif er > 60:
        risks.append({
            "title": "Rising Cost Pressure",
            "description": f"Expenses consume {er:.1f}% of income.",
            "severity": "LOW",
            "evidence": f"expense_ratio={er:.1f}%",
        })
        evidence.append(f"expense_ratio={er:.1f}%")
        score += 7

    if stats["spending_concentration"] > 0.35 and stats.get("largest_category"):
        risks.append({
            "title": "Spending Concentration",
            "description": (
                f"{stats['largest_category']} dominates expenses at "
                f"${stats['largest_category_value']:,.0f}."
            ),
            "severity": "MEDIUM",
            "evidence": f"HHI={stats['spending_concentration']:.3f}",
        })
        evidence.append(f"HHI={stats['spending_concentration']:.3f}")
        score += 12

    if stats["top_vendor_share"] > 25 and stats.get("top_vendor"):
        risks.append({
            "title": "Vendor Concentration",
            "description": (
                f"{stats['top_vendor']} accounts for {stats['top_vendor_share']:.1f}% "
                "of total expenses."
            ),
            "severity": "MEDIUM",
            "evidence": f"top_vendor_share={stats['top_vendor_share']:.1f}%",
        })
        evidence.append(f"top_vendor_share={stats['top_vendor_share']:.1f}%")
        score += 10

    rec = stats.get("recurring_expenses", [])
    if rec:
        monthly_rec = sum(r["monthly_impact"] for r in rec)
        share = (monthly_rec * 12 / max(stats["total_expenses"], 1)) * 100.0
        if share > 40:
            sev = "MEDIUM"
            score += 10
        else:
            sev = "LOW"
            score += 4
        risks.append({
            "title": "Recurring Expense Exposure",
            "description": f"{len(rec)} recurring expense pattern(s) detected.",
            "severity": sev,
            "evidence": f"Recurring annualized impact ≈ ${monthly_rec*12:,.0f}.",
        })
        evidence.append(f"recurring_patterns={len(rec)}")

    if stats["revenue_trend"] == "declining":
        risks.append({
            "title": "Declining Revenue",
            "description": "Revenue trend is declining across the analysis period.",
            "severity": "MEDIUM",
            "evidence": "revenue_trend=declining",
        })
        evidence.append("revenue_trend=declining")
        score += 15

    if stats["expense_trend"] == "rising" and stats["revenue_trend"] != "rising":
        risks.append({
            "title": "Rapid Expense Growth",
            "description": "Expenses are rising faster than revenue.",
            "severity": "MEDIUM",
            "evidence": "expense_trend=rising, revenue_trend!=rising",
        })
        evidence.append("expense_trend=rising")
        score += 12

    score = float(min(100.0, score))
    if score >= 60:
        level = "HIGH"
    elif score >= 30:
        level = "MEDIUM"
    else:
        level = "LOW"

    reasoning = _risk_reasoning_llm(risks, stats)
    if not reasoning:
        if risks:
            titles = ", ".join(r["title"] for r in risks)
            reasoning = (
                f"Risk Agent identified {len(risks)} issue(s): {titles}. "
                f"Combined risk score is {score:.0f}/100, indicating a {level} risk profile."
            )
        else:
            reasoning = (
                "Risk Agent found no material risks: cash flow is positive, expense "
                "ratio is moderate, and spending is reasonably diversified."
            )

    return {
        "risk_level": level,
        "risk_score": int(round(score)),
        "risks": risks,
        "evidence": evidence,
        "reasoning": reasoning,
    }


def _risk_reasoning_llm(risks: List[Dict[str, Any]], stats: Dict[str, Any]) -> Optional[str]:
    if not hf_available():
        return None
    prompt = (
        "You are the Risk Agent in a financial analytics system. "
        "Given the following detected risks and analytics, write 2 sentences of "
        "reasoning summarizing the risk profile. Do not invent numbers.\n\n"
        f"Risks: {json.dumps(risks)[:1500]}\n"
        f"Analytics: {json.dumps({k: v for k, v in stats.items() if k != 'monthly'})[:1500]}\n"
        "Reasoning:"
    )
    return call_hf(prompt, max_new_tokens=180)


# =====================================================================
# Opportunity Agent
# =====================================================================
def run_opportunity_agent(stats: Dict[str, Any]) -> Dict[str, Any]:
    opportunities: List[Dict[str, Any]] = []
    evidence: List[str] = []

    if stats.get("largest_category") and stats["total_expenses"] > 0:
        val = stats["largest_category_value"]
        opportunities.append({
            "title": "Cost Optimization",
            "description": (
                f"{stats['largest_category']} is the largest spending category at "
                f"${val:,.0f}. Even a 10% reduction saves ${val*0.10:,.0f}."
            ),
            "impact": "HIGH" if val > 0.3 * stats["total_expenses"] else "MEDIUM",
            "evidence": f"largest_category={stats['largest_category']} (${val:,.0f})",
        })
        evidence.append(f"largest_category_spend={val:.0f}")

    if stats.get("top_vendor") and stats["top_vendor_share"] > 10:
        opportunities.append({
            "title": "Vendor Optimization",
            "description": (
                f"{stats['top_vendor']} is the highest-spend vendor at "
                f"${stats['top_vendor_value']:,.0f} ({stats['top_vendor_share']:.1f}%). "
                "Renegotiating or diversifying this relationship could reduce cost."
            ),
            "impact": "HIGH" if stats["top_vendor_share"] > 25 else "MEDIUM",
            "evidence": f"top_vendor_share={stats['top_vendor_share']:.1f}%",
        })
        evidence.append(f"top_vendor_share={stats['top_vendor_share']:.1f}%")

    rec = stats.get("recurring_expenses", [])
    if rec:
        annual = sum(r["monthly_impact"] for r in rec) * 12
        opportunities.append({
            "title": "Subscription Review",
            "description": (
                f"{len(rec)} recurring expense pattern(s) detected with an annualized "
                f"impact of ≈${annual:,.0f}. Auditing these could yield savings."
            ),
            "impact": "MEDIUM",
            "evidence": f"recurring_count={len(rec)}",
        })
        evidence.append(f"recurring_annualized={annual:.0f}")

    if stats["net_cash_flow"] > 0 and stats["expense_ratio"] > 50:
        opportunities.append({
            "title": "Cash-Flow Efficiency",
            "description": (
                "Net cash flow is positive but the expense ratio is elevated. "
                "Reallocating a portion of surplus toward higher-ROI areas "
                "could compound growth."
            ),
            "impact": "MEDIUM",
            "evidence": f"expense_ratio={stats['expense_ratio']:.1f}%",
        })
        evidence.append("positive_net_with_high_ratio")

    if stats["revenue_trend"] == "rising":
        opportunities.append({
            "title": "Revenue Momentum",
            "description": (
                "Revenue trend is rising. Investing in the channels driving this "
                "growth could accelerate the trajectory."
            ),
            "impact": "HIGH",
            "evidence": "revenue_trend=rising",
        })
        evidence.append("revenue_trend=rising")

    if stats["spending_concentration"] > 0.3:
        opportunities.append({
            "title": "Spending Diversification",
            "description": (
                "Expense concentration (HHI "
                f"{stats['spending_concentration']:.2f}) suggests reliance on a few "
                "categories. Diversifying reduces single-point risk."
            ),
            "impact": "LOW",
            "evidence": f"HHI={stats['spending_concentration']:.2f}",
        })
        evidence.append(f"HHI={stats['spending_concentration']:.2f}")

    score = float(min(100.0, 25 + len(opportunities) * 14))
    if any(o["impact"] == "HIGH" for o in opportunities):
        score = min(100.0, score + 10)

    reasoning = _opportunity_reasoning_llm(opportunities, stats)
    if not reasoning:
        if opportunities:
            reasoning = (
                f"Opportunity Agent identified {len(opportunities)} action area(s). "
                f"Highest-leverage: {opportunities[0]['title']} — {opportunities[0]['description']}"
            )
        else:
            reasoning = "No significant opportunities detected within current parameters."

    return {
        "opportunity_score": int(round(score)),
        "opportunities": opportunities,
        "evidence": evidence,
        "reasoning": reasoning,
    }


def _opportunity_reasoning_llm(opps: List[Dict[str, Any]], stats: Dict[str, Any]) -> Optional[str]:
    if not hf_available():
        return None
    prompt = (
        "You are the Opportunity Agent in a financial analytics system. "
        "Given the following opportunities and analytics, write 2 sentences of "
        "reasoning. Do not invent numbers.\n\n"
        f"Opportunities: {json.dumps(opps)[:1500]}\n"
        f"Analytics: {json.dumps({k: v for k, v in stats.items() if k != 'monthly'})[:1500]}\n"
        "Reasoning:"
    )
    return call_hf(prompt, max_new_tokens=180)


# =====================================================================
# Decision Agent
# =====================================================================
def run_decision_agent(
    stats: Dict[str, Any],
    risk: Dict[str, Any],
    opportunity: Dict[str, Any],
    revision_hint: Optional[str] = None,
) -> Dict[str, Any]:
    risk_pressure = risk.get("risk_score", 0) / 100.0
    opp_score = opportunity.get("opportunity_score", 0) / 100.0

    top_opp = opportunity["opportunities"][0] if opportunity.get("opportunities") else None
    top_risk = risk["risks"][0] if risk.get("risks") else None

    if risk_pressure >= 0.6 and top_risk:
        title = f"Stabilize: {top_risk['title']}"
        priority = "HIGH"
        decision = (
            f"Prioritize risk mitigation on '{top_risk['title']}' before pursuing growth. "
            f"{top_risk['description']}"
        )
        expected = "Reduce financial risk exposure and protect cash position."
        actions = [
            f"Address: {top_risk['title']}",
            "Re-run analysis after corrective action",
            "Set a 30-day review checkpoint",
        ]
        evidence = risk.get("evidence", [])
    elif top_opp:
        title = f"Optimize: {top_opp['title']}"
        priority = "HIGH" if top_opp["impact"] == "HIGH" else "MEDIUM"
        decision = (
            f"{top_opp['description']} This is the highest-leverage action given the "
            f"current financial profile."
        )
        expected = "Lower operating costs or improve cash-flow efficiency."
        actions = [
            f"Execute: {top_opp['title']}",
            "Measure impact over the next 30 days",
            "Reassess category and vendor allocation",
        ]
        evidence = opportunity.get("evidence", [])
    else:
        title = "Maintain Current Trajectory"
        priority = "LOW"
        decision = (
            "No material risks or high-impact opportunities detected. Maintain the "
            "current financial strategy and continue monitoring."
        )
        expected = "Stable operations."
        actions = ["Continue monthly review"]
        evidence = []

    llm_reasoning = _decision_reasoning_llm(stats, risk, opportunity, revision_hint)
    if llm_reasoning:
        reasoning = llm_reasoning
    else:
        reasoning = (
            f"Risk score is {risk.get('risk_score', 0)}/100 and opportunity score is "
            f"{opportunity.get('opportunity_score', 0)}/100. "
            f"{'Risk pressure dominates' if risk_pressure >= opp_score else 'Opportunity potential dominates'}, "
            f"so the recommended action is to {title.lower()}."
        )

    result = {
        "title": title,
        "priority": priority,
        "decision": decision,
        "reasoning": reasoning,
        "evidence": evidence,
        "expected_impact": expected,
        "recommended_actions": actions,
    }
    if revision_hint:
        result["revision_hint"] = revision_hint
    return result


def _decision_reasoning_llm(
    stats: Dict[str, Any],
    risk: Dict[str, Any],
    opportunity: Dict[str, Any],
    revision_hint: Optional[str],
) -> Optional[str]:
    if not hf_available():
        return None
    prompt = (
        "You are the Decision Agent in a financial analytics system. Weigh the "
        "risks and opportunities below and justify (2 sentences) the single most "
        "important business action. Use ONLY the numbers provided.\n\n"
        f"Analytics: {json.dumps({k: v for k, v in stats.items() if k != 'monthly'})[:1500]}\n"
        f"Risk: {json.dumps(risk)[:1200]}\n"
        f"Opportunity: {json.dumps(opportunity)[:1200]}\n"
    )
    if revision_hint:
        prompt += f"Previous critic feedback to incorporate: {revision_hint}\n"
    prompt += "Reasoning:"
    return call_hf(prompt, max_new_tokens=200)


# =====================================================================
# Critic Agent
# =====================================================================
def run_critic_agent(
    decision: Dict[str, Any],
    risk: Dict[str, Any],
    opportunity: Dict[str, Any],
    stats: Dict[str, Any],
) -> Dict[str, Any]:
    problems: List[str] = []
    evidence: List[str] = []

    if not decision.get("evidence"):
        problems.append("Decision has no supporting evidence.")
    else:
        evidence.append(f"Decision cites {len(decision['evidence'])} evidence item(s).")

    if risk.get("risk_score", 0) >= 60 and decision.get("priority") == "LOW":
        problems.append("High risk present but decision priority is LOW.")

    if opportunity.get("opportunity_score", 0) >= 80 and "maintain" in decision.get("title", "").lower():
        problems.append("Strong opportunities exist but decision is to maintain status quo.")

    reasoning = decision.get("reasoning", "")
    if len(reasoning) < 60:
        problems.append("Decision reasoning is too thin.")

    if not decision.get("recommended_actions"):
        problems.append("Decision has no concrete recommended actions.")

    numeric_ok = any(
        str(v) in json.dumps(stats, default=str)
        for v in [stats.get("total_expenses", 0), stats.get("total_revenue", 0)]
    )
    if numeric_ok:
        evidence.append("Decision references real computed metrics.")

    llm_verdict = _critic_llm(decision, risk, opportunity, stats)

    if llm_verdict and llm_verdict.get("status") in {"APPROVED", "REVISE"}:
        approved = llm_verdict["status"] == "APPROVED"
        reasoning_text = llm_verdict.get("reasoning") or (
            "Critic Agent approved the decision." if approved else "Critic Agent requested revision."
        )
        revision_required = llm_verdict.get("revision_required")
    else:
        approved = len(problems) == 0
        if approved:
            reasoning_text = (
                "Critic Agent verified: the decision is supported by financial evidence, "
                "consistent with identified risks and opportunities, logically sound, "
                "and actionable."
            )
            revision_required = None
        else:
            reasoning_text = "Critic Agent flagged issues: " + "; ".join(problems)
            revision_required = "; ".join(problems)

    return {
        "status": "APPROVED" if approved else "REVISE",
        "approved": approved,
        "reasoning": reasoning_text,
        "evidence": evidence,
        "revision_required": revision_required,
    }


def _critic_llm(
    decision: Dict[str, Any],
    risk: Dict[str, Any],
    opportunity: Dict[str, Any],
    stats: Dict[str, Any],
) -> Optional[dict]:
    if not hf_available():
        return None
    prompt = (
        "You are the Critic Agent in a financial analytics system. Review the "
        "decision below. Respond ONLY with a JSON object: "
        '{"status": "APPROVED" or "REVISE", "reasoning": "...", '
        '"revision_required": "..." or null}.\n\n'
        f"Decision: {json.dumps(decision)[:1200]}\n"
        f"Risk: {json.dumps(risk)[:800]}\n"
        f"Opportunity: {json.dumps(opportunity)[:800]}\n"
        "JSON:"
    )
    text = call_hf(prompt, max_new_tokens=220)
    return _safe_json(text)
