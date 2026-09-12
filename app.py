"""
FinTrack AI — main entry point.
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path
from typing import Any, Dict

ROOT = Path(__file__).resolve().parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from agents.categorize import run_categorization_agent
from agents.decision import run_decision_with_critique
from agents.insights import run_insight_agent
from agents.strategic_agents import (
    hf_available,
    run_analytics_agent,
    run_opportunity_agent,
    run_risk_agent,
)
from utils.data_processing import load_csv, process_transactions
from utils.financial_state import (
    FinancialState,
    get_financial_state,
    reset_financial_state,
)
from utils.ui import inject_auto_nav_hider, render_sidebar

st.set_page_config(
    page_title="FinTrack AI — Agentic Financial Analytics",
    page_icon="💠",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_auto_nav_hider()

CSS = """
<style>
:root {
    --ft-blue: #2563eb;
    --ft-blue-soft: #eff6ff;
    --ft-navy: #0f172a;
    --ft-slate: #475569;
    --ft-muted: #94a3b8;
    --ft-border: #e2e8f0;
    --ft-bg: #ffffff;
    --ft-bg-soft: #f8fafc;
    --ft-green: #10b981;
    --ft-amber: #f59e0b;
    --ft-red: #ef4444;
    --ft-shadow: 0 1px 2px rgba(15, 23, 42, 0.04), 0 4px 16px rgba(15, 23, 42, 0.06);
    --ft-shadow-lg: 0 4px 12px rgba(15, 23, 42, 0.06), 0 16px 40px rgba(15, 23, 42, 0.08);
}

html, body, [class*="css"] {
    font-family: -apple-system, BlinkMacSystemFont, "Inter", "Segoe UI", Roboto, sans-serif;
    color: var(--ft-navy);
}

.main .block-container {
    padding-top: 1.5rem;
    padding-bottom: 3rem;
    max-width: 1280px;
}

#MainMenu {visibility: hidden;}
footer {visibility: hidden;}
header[data-testid="stHeader"] {background: transparent;}

section[data-testid="stSidebar"] {
    background: #ffffff;
    border-right: 1px solid var(--ft-border);
}
section[data-testid="stSidebar"] > div { padding-top: 1.5rem; }

.ft-brand {
    display: flex; align-items: center; gap: 10px;
    font-weight: 800; font-size: 1.15rem; letter-spacing: -0.02em;
    color: var(--ft-navy);
}
.ft-brand .dot {
    width: 30px; height: 30px; border-radius: 9px;
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    display: flex; align-items: center; justify-content: center;
    color: white; font-size: 0.85rem; font-weight: 700;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3);
}
.ft-tagline {
    color: var(--ft-muted); font-size: 0.78rem; margin-top: 2px;
    letter-spacing: 0.02em; text-transform: uppercase; font-weight: 600;
}
.ft-divider {
    height: 1px; background: var(--ft-border); margin: 1.1rem 0;
}
.ft-status {
    display: flex; align-items: center; gap: 8px;
    font-size: 0.82rem; color: var(--ft-slate); font-weight: 600;
    padding: 8px 12px; border-radius: 10px;
    background: var(--ft-bg-soft); border: 1px solid var(--ft-border);
}
.ft-status .pulse {
    width: 8px; height: 8px; border-radius: 50%;
    background: var(--ft-green);
    box-shadow: 0 0 0 3px rgba(16,185,129,0.18);
    animation: pulse 2s infinite;
}
@keyframes pulse {
    0%,100% { opacity: 1; }
    50% { opacity: 0.5; }
}

.ft-card {
    background: var(--ft-bg);
    border: 1px solid var(--ft-border);
    border-radius: 16px;
    padding: 20px 22px;
    box-shadow: var(--ft-shadow);
    transition: box-shadow .2s ease, transform .2s ease;
}
.ft-card:hover { box-shadow: var(--ft-shadow-lg); }

.ft-kpi-label {
    font-size: 0.76rem; text-transform: uppercase; letter-spacing: 0.08em;
    color: var(--ft-muted); font-weight: 700; margin-bottom: 8px;
}
.ft-kpi-value {
    font-size: 1.7rem; font-weight: 800; color: var(--ft-navy);
    letter-spacing: -0.02em; line-height: 1.1;
}
.ft-kpi-sub {
    font-size: 0.8rem; color: var(--ft-slate); margin-top: 6px;
}
.ft-kpi-accent { color: var(--ft-blue); }
.ft-kpi-green { color: var(--ft-green); }
.ft-kpi-red { color: var(--ft-red); }

.ft-h1 {
    font-size: 1.9rem; font-weight: 800; color: var(--ft-navy);
    letter-spacing: -0.025em; margin: 0;
}
.ft-sub { color: var(--ft-slate); font-size: 0.95rem; margin-top: 4px; }

.ft-badge {
    display: inline-flex; align-items: center; gap: 6px;
    padding: 5px 11px; border-radius: 999px;
    font-size: 0.75rem; font-weight: 700; letter-spacing: 0.02em;
    background: rgba(16,185,129,0.1); color: #047857;
    border: 1px solid rgba(16,185,129,0.22);
}
.ft-badge-blue {
    background: var(--ft-blue-soft); color: var(--ft-blue);
    border: 1px solid rgba(37,99,235,0.2);
}
.ft-badge-red {
    background: rgba(239,68,68,0.1); color: #b91c1c;
    border: 1px solid rgba(239,68,68,0.25);
}

.ft-decision {
    background: linear-gradient(135deg, #f8fbff 0%, #eef5ff 100%);
    border: 1px solid #cfe0ff;
    border-radius: 18px;
    padding: 24px 26px;
    box-shadow: var(--ft-shadow-lg);
}
.ft-decision-label {
    font-size: 0.72rem; font-weight: 800; letter-spacing: 0.12em;
    color: var(--ft-blue); text-transform: uppercase; margin-bottom: 8px;
}
.ft-decision-title {
    font-size: 1.35rem; font-weight: 800; color: var(--ft-navy);
    letter-spacing: -0.02em; margin-bottom: 10px;
}
.ft-decision-body { color: var(--ft-slate); font-size: 0.92rem; line-height: 1.55; }
.ft-decision-grid {
    display: grid; grid-template-columns: 1fr 1fr; gap: 16px; margin-top: 18px;
}
.ft-decision-mini {
    background: #fff; border: 1px solid var(--ft-border);
    border-radius: 12px; padding: 14px 16px;
}
.ft-decision-mini .lbl {
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em;
    color: var(--ft-muted); text-transform: uppercase; margin-bottom: 6px;
}
.ft-decision-mini .val { color: var(--ft-navy); font-size: 0.88rem; font-weight: 600; line-height: 1.45; }

.ft-timeline { position: relative; padding-left: 6px; }
.ft-tl-item {
    display: flex; gap: 14px; padding: 12px 0;
    border-bottom: 1px dashed var(--ft-border);
}
.ft-tl-item:last-child { border-bottom: none; }
.ft-tl-icon {
    width: 30px; height: 30px; border-radius: 9px; flex-shrink: 0;
    display: flex; align-items: center; justify-content: center;
    font-size: 0.85rem; font-weight: 700;
    background: rgba(16,185,129,0.12); color: #047857;
}
.ft-tl-icon.pending { background: var(--ft-bg-soft); color: var(--ft-muted); }
.ft-tl-icon.revise { background: rgba(245,158,11,0.14); color: #b45309; }
.ft-tl-name { font-weight: 700; color: var(--ft-navy); font-size: 0.9rem; }
.ft-tl-msg { color: var(--ft-slate); font-size: 0.83rem; margin-top: 2px; }

.ft-item {
    border: 1px solid var(--ft-border); border-radius: 14px;
    padding: 16px 18px; background: #fff; margin-bottom: 12px;
    box-shadow: var(--ft-shadow);
}
.ft-item-title { font-weight: 700; color: var(--ft-navy); font-size: 0.95rem; }
.ft-item-desc { color: var(--ft-slate); font-size: 0.86rem; margin-top: 6px; line-height: 1.5; }
.ft-sev {
    display: inline-block; padding: 3px 9px; border-radius: 999px;
    font-size: 0.7rem; font-weight: 700; letter-spacing: 0.04em;
    margin-left: 8px;
}
.ft-sev-HIGH { background: rgba(239,68,68,0.12); color: #b91c1c; }
.ft-sev-MEDIUM { background: rgba(245,158,11,0.12); color: #b45309; }
.ft-sev-LOW { background: rgba(16,185,129,0.12); color: #047857; }

.ft-hero {
    background: linear-gradient(135deg, #ffffff 0%, #f2f7ff 100%);
    border: 1px solid var(--ft-border);
    border-radius: 20px;
    padding: 40px 44px;
    box-shadow: var(--ft-shadow);
    margin-bottom: 22px;
}
.ft-hero h1 {
    font-size: 2.2rem; font-weight: 800; color: var(--ft-navy);
    letter-spacing: -0.03em; margin: 0 0 8px 0;
}
.ft-hero p { color: var(--ft-slate); font-size: 1rem; line-height: 1.6; margin: 0; max-width: 640px; }

.stButton > button {
    border-radius: 10px; font-weight: 600; border: 1px solid var(--ft-border);
    background: #fff; color: var(--ft-navy);
    transition: all .15s ease;
}
.stButton > button:hover { border-color: var(--ft-blue); color: var(--ft-blue); }
.stButton > button[kind="primary"] {
    background: linear-gradient(135deg, #2563eb, #3b82f6);
    color: #fff; border: none;
    box-shadow: 0 4px 14px rgba(37,99,235,0.28);
}
.stButton > button[kind="primary"]:hover { box-shadow: 0 6px 20px rgba(37,99,235,0.36); }

[data-testid="stDataFrame"] { border: 1px solid var(--ft-border); border-radius: 12px; overflow: hidden; }

.stTabs [data-baseweb="tab-list"] { gap: 6px; }
.stTabs [data-baseweb="tab"] {
    border-radius: 9px 9px 0 0; font-weight: 600; color: var(--ft-slate);
}
.stTabs [aria-selected="true"] { color: var(--ft-blue) !important; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def _get_state() -> FinancialState:
    return get_financial_state()


def _reset_state() -> None:
    reset_financial_state()


def _get_config() -> Dict[str, bool]:
    st.session_state.setdefault("config", {
        "use_ai_categorization": True,
        "use_ai_insights": True,
        "use_vector_db": True,
        "embedding_model": "sentence-transformers/all-MiniLM-L6-v2",
    })
    return st.session_state.config


def fmt_money(v: float) -> str:
    sign = "-" if v < 0 else ""
    return f"{sign}${abs(v):,.0f}"


def fmt_pct(v: float) -> str:
    return f"{v:.1f}%"


def kpi_card(label: str, value: str, sub: str = "", accent: str = "") -> str:
    accent_class = {
        "blue": "ft-kpi-accent",
        "green": "ft-kpi-green",
        "red": "ft-kpi-red",
    }.get(accent, "")
    return f"""
    <div class="ft-card">
        <div class="ft-kpi-label">{label}</div>
        <div class="ft-kpi-value {accent_class}">{value}</div>
        <div class="ft-kpi-sub">{sub}</div>
    </div>
    """


def severity_badge(sev: str) -> str:
    sev = (sev or "LOW").upper()
    return f'<span class="ft-sev ft-sev-{sev}">{sev}</span>'


def _render_progress(placeholder, state: FinancialState) -> None:
    icons = {
        "pending": ("○", "pending"),
        "running": ("◐", "pending"),
        "complete": ("✓", "complete"),
        "revise": ("↻", "revise"),
        "error": ("✕", "revise"),
    }
    rows = []
    for name, status in state.agent_status.items():
        icon, css = icons.get(status["status"], ("○", "pending"))
        msg = status.get("message") or {
            "pending": "Pending",
            "running": "Working…",
            "complete": "Complete",
            "revise": "Revision required",
            "error": "Error",
        }.get(status["status"], "")
        rows.append(
            f'<div class="ft-tl-item">'
            f'<div class="ft-tl-icon {css}">{icon}</div>'
            f'<div><div class="ft-tl-name">{name}</div>'
            f'<div class="ft-tl-msg">{msg}</div></div>'
            f'</div>'
        )
    placeholder.markdown(
        f'<div class="ft-card"><div class="ft-timeline">{"".join(rows)}</div></div>',
        unsafe_allow_html=True,
    )


def _run_pipeline(df_raw: pd.DataFrame, progress_placeholder) -> FinancialState:
    state = _get_state()
    config = _get_config()
    state.errors = []

    state.set_status("Data Agent", "running")
    _render_progress(progress_placeholder, state)
    try:
        result = process_transactions(df_raw)
    except Exception as exc:
        state.set_status("Data Agent", "error", str(exc))
        state.errors.append(str(exc))
        _render_progress(progress_placeholder, state)
        return state

    state.df = result["df"]
    state.quality = result["quality"]
    state.errors.extend(result["errors"])
    state.set_status(
        "Data Agent", "complete",
        f"{state.quality['clean_rows']} transactions cleaned",
        "; ".join(result["errors"]) or "All rows valid.",
    )
    time.sleep(0.1)
    _render_progress(progress_placeholder, state)

    if state.df.empty:
        state.set_status("Data Agent", "error", "No valid rows after cleaning.")
        _render_progress(progress_placeholder, state)
        return state

    state.set_status("Categorization Agent", "running")
    _render_progress(progress_placeholder, state)
    cat = run_categorization_agent(state.df, use_ai=config["use_ai_categorization"])
    state.df = cat["df"]
    state.set_status(
        "Categorization Agent", "complete",
        f"{cat['classified']} transactions classified",
        f"Method: {cat['method']} • categories: {len(cat['counts'])}",
    )
    time.sleep(0.1)
    _render_progress(progress_placeholder, state)

    state.set_status("Analytics Agent", "running")
    _render_progress(progress_placeholder, state)
    state.stats = run_analytics_agent(state.df)
    state.set_status(
        "Analytics Agent", "complete",
        f"{len(state.stats['evidence'])} financial patterns analyzed",
        f"Revenue {fmt_money(state.stats['total_revenue'])} • "
        f"Expenses {fmt_money(state.stats['total_expenses'])}",
    )
    time.sleep(0.1)
    _render_progress(progress_placeholder, state)

    state.set_status("Risk Agent", "running")
    _render_progress(progress_placeholder, state)
    state.risk = run_risk_agent(state.stats)
    state.set_status(
        "Risk Agent", "complete",
        f"{len(state.risk['risks'])} risk(s) detected",
        f"Risk level: {state.risk['risk_level']} ({state.risk['risk_score']}/100)",
    )
    time.sleep(0.1)
    _render_progress(progress_placeholder, state)

    state.set_status("Opportunity Agent", "running")
    _render_progress(progress_placeholder, state)
    state.opportunity = run_opportunity_agent(state.stats)
    state.set_status(
        "Opportunity Agent", "complete",
        f"{len(state.opportunity['opportunities'])} opportunit(ies) identified",
        f"Opportunity score: {state.opportunity['opportunity_score']}/100",
    )
    time.sleep(0.1)
    _render_progress(progress_placeholder, state)

    state.set_status("Decision Agent", "running")
    _render_progress(progress_placeholder, state)
    decision, critic, revisions, loop_summary = run_decision_with_critique(
        state.stats, state.risk, state.opportunity
    )
    state.decision = decision
    state.critic = critic
    state.revision_count = revisions

    state.set_status(
        "Decision Agent", "complete",
        decision.get("title", "Decision made"),
        f"Priority: {decision.get('priority', '—')}",
    )
    if revisions > 0:
        state.set_status(
            "Critic Agent", "complete",
            f"Decision revised {revisions}× then approved",
            loop_summary,
        )
    else:
        state.set_status(
            "Critic Agent", "complete",
            "Decision verified",
            loop_summary,
        )
    time.sleep(0.1)
    _render_progress(progress_placeholder, state)

    state.set_status("Insight Agent", "running")
    _render_progress(progress_placeholder, state)
    health_score = state.financial_health_score()
    health_label = state.health_label()
    state.summary = run_insight_agent(
        state.stats, state.risk, state.opportunity,
        state.decision, state.critic,
        health_score, health_label,
        use_ai=config["use_ai_insights"],
    )
    state.set_status(
        "Insight Agent", "complete",
        "Financial briefing generated",
        f"Health: {health_score}/100 — {health_label}",
    )
    time.sleep(0.1)
    _render_progress(progress_placeholder, state)

    return state


def cash_flow_chart(monthly: list) -> go.Figure:
    if not monthly:
        return go.Figure()
    months = [m["month"] for m in monthly]
    rev = [m["revenue"] for m in monthly]
    exp = [m["expenses"] for m in monthly]
    net = [m["net"] for m in monthly]

    fig = go.Figure()
    fig.add_bar(x=months, y=rev, name="Revenue", marker_color="#93c5fd", marker_line_width=0)
    fig.add_bar(x=months, y=exp, name="Expenses", marker_color="#fca5a5", marker_line_width=0)
    fig.add_trace(go.Scatter(
        x=months, y=net, name="Net Cash Flow",
        mode="lines+markers",
        line=dict(color="#2563eb", width=3),
        marker=dict(size=9, color="#2563eb", line=dict(color="white", width=2)),
    ))
    fig.update_layout(
        barmode="group",
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#334155", size=12),
        margin=dict(l=10, r=10, t=10, b=10),
        height=340,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, bgcolor="rgba(0,0,0,0)"),
        xaxis=dict(showgrid=False, linecolor="#e2e8f0"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9", zerolinecolor="#cbd5e1", tickprefix="$", tickformat=",.0f"),
        hoverlabel=dict(bgcolor="white", bordercolor="#e2e8f0", font_size=12),
    )
    return fig


def health_gauge(score: int, label: str) -> go.Figure:
    color = (
        "#10b981" if score >= 80 else
        "#22c55e" if score >= 60 else
        "#f59e0b" if score >= 40 else "#ef4444"
    )
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": " / 100", "font": {"size": 30, "color": "#0f172a", "family": "Inter"}},
            gauge={
                "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#cbd5e1",
                         "tickfont": {"size": 10, "color": "#94a3b8"}},
                "bar": {"color": color, "thickness": 0.28},
                "bgcolor": "#f1f5f9",
                "borderwidth": 0,
                "steps": [
                    {"range": [0, 40], "color": "rgba(239,68,68,0.08)"},
                    {"range": [40, 60], "color": "rgba(245,158,11,0.08)"},
                    {"range": [60, 80], "color": "rgba(34,197,94,0.08)"},
                    {"range": [80, 100], "color": "rgba(16,185,129,0.10)"},
                ],
            },
        )
    )
    fig.update_layout(
        height=210, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor="white", font=dict(family="Inter, sans-serif"),
    )
    return fig


def render_landing() -> None:
    st.markdown(
        """
        <div class="ft-hero">
            <div class="ft-badge ft-badge-blue" style="margin-bottom:14px;">
                ● AGENTIC FINANCIAL DECISION SYSTEM
            </div>
            <h1>Your AI Financial Decision Engine</h1>
            <p>
                Upload your financial data. Specialized AI agents analyze it,
                challenge each other's conclusions, and recommend what your
                business should do next — with a Critic Agent verifying every
                strategic decision before it reaches you.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1.4, 1])

    with col1:
        st.markdown("#### Upload your transactions")
        uploaded = st.file_uploader(
            "CSV with columns: date, description, amount",
            type=["csv"],
            label_visibility="collapsed",
        )
        st.markdown(
            "<div style='color:#64748b;font-size:0.82rem;margin-top:6px;'>"
            "Positive amounts = income · Negative amounts = expenses"
            "</div>",
            unsafe_allow_html=True,
        )
        st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
        use_sample = st.button("Try sample data", use_container_width=True)
        st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
        start = st.button("Run AI Analysis", type="primary", use_container_width=True)

    with col2:
        st.markdown(
            """
            <div class="ft-card" style="height:100%;">
                <div class="ft-kpi-label">The Agentic Pipeline</div>
                <div style="margin-top:10px;color:#334155;font-size:0.88rem;line-height:2;">
                    <div>🔹 Data Agent — cleans &amp; validates</div>
                    <div>🔹 Categorization Agent — classifies</div>
                    <div>🔹 Analytics Agent — computes patterns</div>
                    <div>🔹 Risk Agent — finds risks</div>
                    <div>🔹 Opportunity Agent — finds upside</div>
                    <div>🔹 Decision Agent — decides</div>
                    <div>🔹 <b>Critic Agent — verifies or revises</b></div>
                    <div>🔹 Insight Agent — briefs you</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    df_raw = None
    if start:
        if uploaded is not None:
            try:
                df_raw = load_csv(uploaded.getvalue())
            except Exception as exc:
                st.error(f"Could not read file: {exc}")
        elif use_sample:
            try:
                df_raw = load_csv("sample_data/sample_transactions.csv")
            except Exception as exc:
                st.error(f"Could not load sample data: {exc}")
        else:
            st.warning("Please upload a CSV or click 'Try sample data' first.")

    if df_raw is not None:
        _execute_analysis(df_raw)


def _execute_analysis(df_raw: pd.DataFrame) -> None:
    st.markdown("### Analyzing your financial data…")
    progress_placeholder = st.empty()
    state = _get_state()

    with st.spinner("Agents are working…"):
        state = _run_pipeline(df_raw, progress_placeholder)

    if state.errors and state.df is None:
        st.error("Analysis failed: " + "; ".join(state.errors))
        return

    st.success("Analysis complete. Open a page from the sidebar to explore results.")
    st.session_state["analysis_done"] = True
    time.sleep(0.3)
    st.rerun()


def render_overview(state: FinancialState) -> None:
    if not state.is_complete():
        st.info("No analysis yet. Go to **Overview** and run an analysis to populate this page.")
        return

    stats = state.stats
    health_score = state.financial_health_score()
    health_label = state.health_label()

    head_l, head_r = st.columns([3, 1])
    with head_l:
        st.markdown(
            """
            <div>
                <div class="ft-h1">Financial Intelligence</div>
                <div class="ft-sub">AI-powered financial analysis for your business</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with head_r:
        st.markdown(
            f"""
            <div style="text-align:right;">
                <span class="ft-badge">● AI Analysis Complete</span>
                <div style="color:#94a3b8;font-size:0.78rem;margin-top:6px;">
                    {stats['num_transactions']} transactions analyzed
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(kpi_card("Revenue", fmt_money(stats["total_revenue"]),
                             "Income across all periods", accent="blue"), unsafe_allow_html=True)
    with c2:
        st.markdown(kpi_card("Expenses", fmt_money(stats["total_expenses"]),
                             f"Across {len(stats.get('category_totals', {}))} categories",
                             accent="red"), unsafe_allow_html=True)
    with c3:
        net = stats["net_cash_flow"]
        st.markdown(kpi_card("Net Cash Flow", fmt_money(net), "Revenue − Expenses",
                             accent="green" if net >= 0 else "red"), unsafe_allow_html=True)
    with c4:
        st.markdown(kpi_card("Expense Ratio", fmt_pct(stats["expense_ratio"]),
                             "Expenses as % of revenue",
                             accent="green" if stats["expense_ratio"] < 60 else "red"),
                    unsafe_allow_html=True)

    st.markdown("<div style='height:18px'></div>", unsafe_allow_html=True)

    left, right = st.columns([1, 1.6])

    with left:
        st.markdown('<div class="ft-card"><div class="ft-kpi-label">Financial Health</div></div>',
                    unsafe_allow_html=True)
        st.plotly_chart(health_gauge(health_score, health_label),
                        use_container_width=True, config={"displayModeBar": False})
        st.markdown(
            f"""
            <div style="margin-top:-12px;text-align:center;">
                <span class="ft-badge {'ft-badge-red' if health_score < 40 else ''}">
                    ● {health_label}
                </span>
                <div style="color:#64748b;font-size:0.8rem;margin-top:8px;">
                    Based on cash flow, expense ratio, spending patterns and detected risks.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        d = state.decision
        c = state.critic
        critic_icon = "✓" if c.get("approved") else "↻"
        critic_txt = "Decision Verified" if c.get("approved") else "Revision Required"
        revision_line = (
            f'<div style="color:#b45309;font-size:0.8rem;margin-top:10px;">'
            f'↻ {state.revision_count} revision(s) applied before approval.</div>'
            if state.revision_count > 0 else
            f'<div style="color:#047857;font-size:0.8rem;margin-top:10px;">'
            f'✓ Approved on first pass.</div>'
        )
        st.markdown(
            f"""
            <div class="ft-decision">
                <div class="ft-decision-label">AI DECISION &nbsp;·&nbsp; {critic_icon} {critic_txt}</div>
                <div class="ft-decision-title">{d.get('title', '—')}</div>
                <div class="ft-decision-body">{d.get('decision', '')}</div>
                <div class="ft-decision-grid">
                    <div class="ft-decision-mini">
                        <div class="lbl">Recommended Action</div>
                        <div class="val">{d.get('recommended_actions', ['—'])[0]}</div>
                    </div>
                    <div class="ft-decision-mini">
                        <div class="lbl">Expected Impact</div>
                        <div class="val">{d.get('expected_impact', '—')}</div>
                    </div>
                </div>
                {revision_line}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)

    st.markdown('<div class="ft-kpi-label">Cash Flow Trend</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-card">', unsafe_allow_html=True)
    st.plotly_chart(cash_flow_chart(stats["monthly"]),
                    use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="ft-kpi-label">Agent Intelligence</div>', unsafe_allow_html=True)

    rows = []
    for name, s in state.agent_status.items():
        status = s["status"]
        icon = {"complete": "✓", "running": "◐", "pending": "○", "error": "✕", "revise": "↻"}.get(status, "○")
        css = "pending" if status in {"pending", "running"} else ("revise" if status in {"error", "revise"} else "")
        msg = s.get("message") or status.title()
        detail = s.get("detail", "")
        detail_html = f'<div class="ft-tl-msg" style="font-size:0.78rem;color:#94a3b8;">{detail}</div>' if detail else ""
        rows.append(
            f'<div class="ft-tl-item">'
            f'<div class="ft-tl-icon {css}">{icon}</div>'
            f'<div><div class="ft-tl-name">{name}</div>'
            f'<div class="ft-tl-msg">{msg}</div>{detail_html}</div>'
            f'</div>'
        )
    st.markdown(
        f'<div class="ft-card"><div class="ft-timeline">{"".join(rows)}</div></div>',
        unsafe_allow_html=True,
    )

    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    st.markdown('<div class="ft-kpi-label">Risks & Opportunities</div>', unsafe_allow_html=True)
    rc, oc = st.columns(2)

    with rc:
        risks = state.risk.get("risks", [])
        if not risks:
            st.markdown(
                '<div class="ft-item"><div class="ft-item-title">No material risks detected</div>'
                '<div class="ft-item-desc">Cash flow, expense ratio, and concentration are within healthy bounds.</div></div>',
                unsafe_allow_html=True,
            )
        for r in risks[:3]:
            st.markdown(
                f'<div class="ft-item">'
                f'<div class="ft-item-title">{r["title"]}{severity_badge(r.get("severity","LOW"))}</div>'
                f'<div class="ft-item-desc">{r["description"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )
    with oc:
        opps = state.opportunity.get("opportunities", [])
        if not opps:
            st.markdown(
                '<div class="ft-item"><div class="ft-item-title">No major opportunities detected</div>'
                '<div class="ft-item-desc">Current spending and cash flow look optimized.</div></div>',
                unsafe_allow_html=True,
            )
        for o in opps[:3]:
            st.markdown(
                f'<div class="ft-item">'
                f'<div class="ft-item-title">↑ {o["title"]}{severity_badge(o.get("impact","LOW"))}</div>'
                f'<div class="ft-item-desc">{o["description"]}</div>'
                f'</div>',
                unsafe_allow_html=True,
            )


def main() -> None:
    state = _get_state()
    render_sidebar()

    if not state.is_complete() and not st.session_state.get("analysis_done"):
        render_landing()
    elif not state.is_complete():
        render_landing()
    else:
        render_overview(state)


if __name__ == "__main__":
    main()
