"""
Agent Center — the complete agentic workflow, visualized.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from utils.financial_state import FinancialState, get_financial_state
from utils.ui import render_sidebar

st.set_page_config(page_title="Agent Center — FinTrack AI", page_icon="🤖", layout="wide")

CSS = """
<style>
.ft-card { background:#fff; border:1px solid #e2e8f0; border-radius:16px;
    padding:20px 22px; box-shadow:0 1px 2px rgba(15,23,42,.04),0 4px 16px rgba(15,23,42,.06); margin-bottom:14px; }
.ft-agent-title { font-size:1.05rem; font-weight:800; color:#0f172a; display:flex;
    align-items:center; gap:10px; letter-spacing:-0.01em; }
.ft-agent-icon { width:34px;height:34px;border-radius:10px;display:flex;align-items:center;
    justify-content:center;font-size:1rem; background:linear-gradient(135deg,#2563eb,#3b82f6); color:#fff;
    box-shadow:0 4px 12px rgba(37,99,235,.28); }
.ft-status-pill { display:inline-block;padding:3px 10px;border-radius:999px;font-size:.7rem;
    font-weight:700;letter-spacing:.04em;text-transform:uppercase; }
.ft-st-complete { background:rgba(16,185,129,.12); color:#047857; }
.ft-st-running  { background:rgba(37,99,235,.12);  color:#1d4ed8; }
.ft-st-pending  { background:#f1f5f9; color:#64748b; }
.ft-st-error    { background:rgba(239,68,68,.12);  color:#b91c1c; }
.ft-row { display:grid; grid-template-columns:140px 1fr; gap:12px; padding:8px 0;
    border-top:1px dashed #e2e8f0; font-size:.86rem; }
.ft-row .k { color:#94a3b8; font-weight:700; text-transform:uppercase; letter-spacing:.06em; font-size:.7rem; }
.ft-row .v { color:#334155; line-height:1.55; }
.ft-arrow { text-align:center; color:#94a3b8; font-size:1.4rem; padding:2px 0; }
.ft-h1 { font-size:1.9rem; font-weight:800; color:#0f172a; letter-spacing:-.025em; margin:0; }
.ft-sub { color:#475569; font-size:.95rem; margin-top:4px; }
.ft-evidence { background:#f8fafc; border:1px solid #e2e8f0; border-radius:10px;
    padding:10px 12px; font-size:.8rem; color:#475569; margin-top:6px; font-family:ui-monospace,Menlo,monospace; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

render_sidebar()


def _status_pill(status: str) -> str:
    cls = {
        "complete": "ft-st-complete",
        "running": "ft-st-running",
        "pending": "ft-st-pending",
        "error": "ft-st-error",
        "revise": "ft-st-error",
    }.get(status, "ft-st-pending")
    return f'<span class="ft-status-pill {cls}">{status}</span>'


def _agent_card(
    name: str, icon: str, responsibility: str, inputs: str, output: str,
    reasoning: str, evidence: str, status: str, status_msg: str,
) -> None:
    st.markdown(
        f"""
        <div class="ft-card">
            <div class="ft-agent-title">
                <div class="ft-agent-icon">{icon}</div>
                <div style="flex:1;">{name}</div>
                {_status_pill(status)}
            </div>
            <div style="color:#64748b;font-size:.85rem;margin:6px 0 12px;">{responsibility}</div>
            <div class="ft-row"><div class="k">Input</div><div class="v">{inputs}</div></div>
            <div class="ft-row"><div class="k">Output</div><div class="v">{output}</div></div>
            <div class="ft-row"><div class="k">Reasoning</div><div class="v">{reasoning}</div></div>
            <div class="ft-row"><div class="k">Evidence</div><div class="v"><div class="ft-evidence">{evidence}</div></div></div>
            <div class="ft-row"><div class="k">Status</div><div class="v">{status_msg or status.title()}</div></div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    state: FinancialState = get_financial_state()

    st.markdown('<div class="ft-h1">Agent Center</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ft-sub">Every agent, its responsibility, its reasoning, and the evidence it used.</div>',
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if not state.agent_status or all(s["status"] == "pending" for s in state.agent_status.values()):
        st.info("Run an analysis on the Overview page to see the agent workflow.")
        return

    st.markdown("#### Agentic Pipeline")
    st.markdown(
        """
        <div class="ft-card" style="text-align:center;font-family:ui-monospace,Menlo,monospace;
             font-size:.85rem;color:#334155;line-height:1.9;">
            <div><b>DATA</b></div>
            <div class="ft-arrow">↓</div>
            <div><b>CATEGORIZE</b></div>
            <div class="ft-arrow">↓</div>
            <div><b>ANALYZE</b></div>
            <div class="ft-arrow">↓</div>
            <div><b>RISK</b> &nbsp;·&nbsp; <b>OPPORTUNITY</b></div>
            <div class="ft-arrow">↓</div>
            <div><b>DECISION</b></div>
            <div class="ft-arrow">↓</div>
            <div><b>CRITIC</b></div>
            <div class="ft-arrow">↓</div>
            <div><b>INSIGHT</b></div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    if state.critic:
        if state.revision_count > 0:
            st.markdown(
                f"""
                <div class="ft-card" style="border-left:4px solid #f59e0b;">
                    <div class="ft-agent-title">
                        <div class="ft-agent-icon" style="background:linear-gradient(135deg,#f59e0b,#fbbf24);">↻</div>
                        <div>Critic Loop — Revision Applied</div>
                    </div>
                    <div style="color:#475569;font-size:.87rem;margin-top:8px;">
                        Decision Agent → Critic Agent → <b>Revision Required</b> → Decision Agent
                        ({state.revision_count} revision(s)) → <b>Approved</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                """
                <div class="ft-card" style="border-left:4px solid #10b981;">
                    <div class="ft-agent-title">
                        <div class="ft-agent-icon" style="background:linear-gradient(135deg,#10b981,#34d399);">✓</div>
                        <div>Critic Loop — Verified</div>
                    </div>
                    <div style="color:#475569;font-size:.87rem;margin-top:8px;">
                        Decision Agent → Critic Agent → <b>✓ Decision Verified</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    a = state.agent_status

    if state.quality:
        _agent_card(
            name="Data Agent", icon="①",
            responsibility="Loads CSV, normalizes columns, validates rows, parses dates and amounts, and reports data quality.",
            inputs="Raw uploaded CSV",
            output=f"{state.quality.get('clean_rows', 0)} clean transactions · "
                   f"{state.quality.get('income_rows', 0)} income / {state.quality.get('expense_rows', 0)} expense",
            reasoning=f"Normalized columns and dropped {state.quality.get('dropped_rows', 0)} invalid row(s). "
                      f"Date range: {state.quality.get('date_range', 'n/a')}.",
            evidence=f"original={state.quality.get('original_rows')} · clean={state.quality.get('clean_rows')} · "
                     f"dropped={state.quality.get('dropped_rows')}",
            status=a["Data Agent"]["status"], status_msg=a["Data Agent"]["message"],
        )

    if state.df is not None and "category" in state.df.columns:
        counts = state.df["category"].value_counts().to_dict()
        _agent_card(
            name="Categorization Agent", icon="②",
            responsibility="Classifies every transaction into one of the fixed categories using Groq or keyword fallback.",
            inputs=f"{len(state.df)} cleaned transactions",
            output=", ".join(f"{k}: {v}" for k, v in list(counts.items())[:5]),
            reasoning="Enforced the category set — no invalid categories can escape. "
                      "AI used when GROQ_API_KEY is present, otherwise deterministic keyword matching.",
            evidence=f"categories={len(counts)} · avg_confidence={state.df['category_confidence'].mean():.2f}",
            status=a["Categorization Agent"]["status"], status_msg=a["Categorization Agent"]["message"],
        )

    if state.stats:
        s = state.stats
        _agent_card(
            name="Analytics Agent", icon="③",
            responsibility="Computes revenue, expenses, cash flow, ratios, monthly series, vendors, recurring expenses, and trends.",
            inputs="Categorized transaction DataFrame",
            output=f"Revenue {s['total_revenue']:,.0f} · Expenses {s['total_expenses']:,.0f} · "
                   f"Net {s['net_cash_flow']:,.0f} · Ratio {s['expense_ratio']:.1f}%",
            reasoning=f"Built {len(s['evidence'])} structured evidence items. "
                      f"Largest category: {s.get('largest_category', 'n/a')}. "
                      f"Top vendor: {s.get('top_vendor', 'n/a')}.",
            evidence="<br>".join(e["interpretation"] for e in s["evidence"][:6]),
            status=a["Analytics Agent"]["status"], status_msg=a["Analytics Agent"]["message"],
        )

    if state.risk:
        r = state.risk
        _agent_card(
            name="Risk Agent", icon="④",
            responsibility="Independently reasons over analytics to detect financial risks, each backed by evidence.",
            inputs="Analytics Agent evidence set",
            output=f"{len(r['risks'])} risk(s) · level {r['risk_level']} · score {r['risk_score']}/100",
            reasoning=r["reasoning"],
            evidence="<br>".join(r["evidence"]) or "No risks — all checks passed.",
            status=a["Risk Agent"]["status"], status_msg=a["Risk Agent"]["message"],
        )

    if state.opportunity:
        o = state.opportunity
        _agent_card(
            name="Opportunity Agent", icon="⑤",
            responsibility="Searches for financial opportunities: cost optimization, vendor renegotiation, subscription review, growth.",
            inputs="Analytics Agent evidence set",
            output=f"{len(o['opportunities'])} opportunity(ies) · score {o['opportunity_score']}/100",
            reasoning=o["reasoning"],
            evidence="<br>".join(o["evidence"]) or "No material opportunities detected.",
            status=a["Opportunity Agent"]["status"], status_msg=a["Opportunity Agent"]["message"],
        )

    if state.decision:
        d = state.decision
        _agent_card(
            name="Decision Agent", icon="⑥",
            responsibility="Weighs risks + opportunities + analytics to choose the single most important business action.",
            inputs="Risk Agent output + Opportunity Agent output + Analytics evidence",
            output=f"{d.get('title', '—')} · priority {d.get('priority', '—')}",
            reasoning=d.get("reasoning", ""),
            evidence="<br>".join(d.get("evidence", [])) or "Evidence attached to decision.",
            status=a["Decision Agent"]["status"], status_msg=a["Decision Agent"]["message"],
        )

    if state.critic:
        c = state.critic
        _agent_card(
            name="Critic Agent", icon="⑦",
            responsibility="Independently verifies the Decision Agent: checks evidence, consistency with risks/opportunities, and practicality.",
            inputs="Decision Agent output + Risk + Opportunity + Analytics",
            output=f"Status: {c.get('status', '—')} · "
                   f"{'Approved' if c.get('approved') else 'Revision required'}",
            reasoning=c.get("reasoning", ""),
            evidence="<br>".join(c.get("evidence", [])) or "Verification checks performed.",
            status=a["Critic Agent"]["status"], status_msg=a["Critic Agent"]["message"],
        )

    if state.summary:
        sm = state.summary
        _agent_card(
            name="Insight Agent", icon="⑧",
            responsibility="Generates the executive financial briefing from the approved decision and full state.",
            inputs="All previous agent outputs",
            output=f"{sm.get('health_score', 0)}/100 — {sm.get('health_label', '')}",
            reasoning=sm.get("narrative", "")[:400] + ("…" if len(sm.get("narrative", "")) > 400 else ""),
            evidence=f"method={sm.get('method', 'deterministic')}",
            status=a["Insight Agent"]["status"], status_msg=a["Insight Agent"]["message"],
        )


main()
