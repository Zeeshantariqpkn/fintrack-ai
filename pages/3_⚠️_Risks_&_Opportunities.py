"""
Risks & Opportunities page — decision-oriented panels.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.graph_objects as go
import streamlit as st

from utils.financial_state import FinancialState, get_financial_state

st.set_page_config(page_title="Risks & Opportunities — FinTrack AI", page_icon="⚠️", layout="wide")

CSS = """
<style>
.ft-h1 { font-size:1.9rem; font-weight:800; color:#0f172a; letter-spacing:-.025em; margin:0; }
.ft-sub { color:#475569; font-size:.95rem; margin-top:4px; }
.ft-kpi-label { font-size:.76rem; text-transform:uppercase; letter-spacing:.08em;
    color:#94a3b8; font-weight:700; margin:14px 0 8px; }
.ft-card { background:#fff; border:1px solid #e2e8f0; border-radius:16px;
    padding:20px 22px; box-shadow:0 1px 2px rgba(15,23,42,.04),0 4px 16px rgba(15,23,42,.06); }
.ft-item { border:1px solid #e2e8f0; border-radius:14px; padding:16px 18px;
    background:#fff; margin-bottom:12px; box-shadow:0 1px 2px rgba(15,23,42,.04); }
.ft-item-title { font-weight:800; color:#0f172a; font-size:.98rem; }
.ft-item-desc { color:#475569; font-size:.87rem; margin-top:6px; line-height:1.55; }
.ft-item-ev { color:#94a3b8; font-size:.78rem; margin-top:8px; font-family:ui-monospace,Menlo,monospace; }
.ft-sev { display:inline-block; padding:3px 9px; border-radius:999px; font-size:.7rem;
    font-weight:700; letter-spacing:.04em; margin-left:8px; }
.ft-sev-HIGH { background:rgba(239,68,68,.12); color:#b91c1c; }
.ft-sev-MEDIUM { background:rgba(245,158,11,.12); color:#b45309; }
.ft-sev-LOW { background:rgba(16,185,129,.12); color:#047857; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def _sev(sev: str) -> str:
    sev = (sev or "LOW").upper()
    return f'<span class="ft-sev ft-sev-{sev}">{sev}</span>'


def _risk_gauge(score: int, level: str) -> go.Figure:
    color = {"HIGH": "#ef4444", "MEDIUM": "#f59e0b", "LOW": "#10b981"}.get(level, "#94a3b8")
    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        number={"suffix": " / 100", "font": {"size": 28, "color": "#0f172a"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#cbd5e1",
                     "tickfont": {"size": 10, "color": "#94a3b8"}},
            "bar": {"color": color, "thickness": 0.28},
            "bgcolor": "#f1f5f9", "borderwidth": 0,
            "steps": [
                {"range": [0, 30], "color": "rgba(16,185,129,0.08)"},
                {"range": [30, 60], "color": "rgba(245,158,11,0.08)"},
                {"range": [60, 100], "color": "rgba(239,68,68,0.08)"},
            ],
        },
    ))
    fig.update_layout(height=200, margin=dict(l=10, r=10, t=10, b=10),
                      paper_bgcolor="white", font=dict(family="Inter, sans-serif"))
    return fig


def main() -> None:
    state: FinancialState = get_financial_state()

    st.markdown('<div class="ft-h1">Risks & Opportunities</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-sub">Decision-oriented view of what could hurt you and what could help you.</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if not state.risk or not state.opportunity:
        st.info("Run an analysis on the Overview page first.")
        return

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown('<div class="ft-kpi-label">Risk Score</div>', unsafe_allow_html=True)
        st.plotly_chart(_risk_gauge(state.risk["risk_score"], state.risk["risk_level"]),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f'<div style="text-align:center;margin-top:-10px;">'
            f'<span class="ft-sev ft-sev-{state.risk["risk_level"]}">'
            f'{state.risk["risk_level"]} RISK</span></div>',
            unsafe_allow_html=True,
        )
    with c2:
        st.markdown('<div class="ft-kpi-label">Opportunity Score</div>', unsafe_allow_html=True)
        st.plotly_chart(_risk_gauge(state.opportunity["opportunity_score"], "LOW"),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f'<div style="text-align:center;margin-top:-10px;">'
            f'<span style="color:#64748b;font-size:.82rem;">'
            f'{len(state.opportunity["opportunities"])} opportunities identified</span></div>',
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
    left, right = st.columns(2)

    with left:
        st.markdown('<div class="ft-kpi-label">Risks</div>', unsafe_allow_html=True)
        if not state.risk["risks"]:
            st.markdown('<div class="ft-card">No material risks detected.</div>', unsafe_allow_html=True)
        for r in state.risk["risks"]:
            st.markdown(
                f'<div class="ft-item">'
                f'<div class="ft-item-title">{r["title"]}{_sev(r.get("severity","LOW"))}</div>'
                f'<div class="ft-item-desc">{r["description"]}</div>'
                f'<div class="ft-item-ev">↳ {r.get("evidence", "")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        if state.risk.get("reasoning"):
            st.markdown(
                f'<div class="ft-card" style="margin-top:10px;">'
                f'<div class="ft-kpi-label">Risk Agent Reasoning</div>'
                f'<div style="color:#475569;font-size:.88rem;line-height:1.6;">{state.risk["reasoning"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    with right:
        st.markdown('<div class="ft-kpi-label">Opportunities</div>', unsafe_allow_html=True)
        if not state.opportunity["opportunities"]:
            st.markdown('<div class="ft-card">No major opportunities detected.</div>', unsafe_allow_html=True)
        for o in state.opportunity["opportunities"]:
            st.markdown(
                f'<div class="ft-item">'
                f'<div class="ft-item-title">↑ {o["title"]}{_sev(o.get("impact","LOW"))}</div>'
                f'<div class="ft-item-desc">{o["description"]}</div>'
                f'<div class="ft-item-ev">↳ {o.get("evidence", "")}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
        if state.opportunity.get("reasoning"):
            st.markdown(
                f'<div class="ft-card" style="margin-top:10px;">'
                f'<div class="ft-kpi-label">Opportunity Agent Reasoning</div>'
                f'<div style="color:#475569;font-size:.88rem;line-height:1.6;">{state.opportunity["reasoning"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    if state.decision:
        st.markdown('<div class="ft-kpi-label">Recommended Actions (from Decision Agent)</div>',
                    unsafe_allow_html=True)
        actions = state.decision.get("recommended_actions", [])
        if actions:
            st.markdown('<div class="ft-card">', unsafe_allow_html=True)
            for i, a in enumerate(actions, 1):
                st.markdown(
                    f'<div style="display:flex;gap:12px;padding:8px 0;'
                    f'border-bottom:1px dashed #e2e8f0;font-size:.9rem;">'
                    f'<div style="width:24px;height:24px;border-radius:7px;'
                    f'background:linear-gradient(135deg,#2563eb,#3b82f6);color:#fff;'
                    f'display:flex;align-items:center;justify-content:center;'
                    f'font-size:.75rem;font-weight:700;flex-shrink:0;">{i}</div>'
                    f'<div style="color:#334155;line-height:1.5;">{a}</div>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)


main()
