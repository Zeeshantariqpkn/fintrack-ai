
import os

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.financial_state import (
    get_financial_state,
    has_financial_state,
    run_financial_analysis,
    save_financial_state,
)


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="FinTrack AI",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================
# PREMIUM UI
# ============================================================

st.markdown(
    """
    <style>

    /* ========================================================
       GLOBAL
    ======================================================== */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }

    header {
        background: transparent !important;
    }

    .block-container {
        max-width: 1500px;
        padding: 28px 42px 50px 42px;
    }

    html, body, [class*="css"] {
        font-family:
            Inter,
            -apple-system,
            BlinkMacSystemFont,
            "Segoe UI",
            sans-serif;
    }

    .stApp {
        background: #f7f9fc;
    }

    /* ========================================================
       SIDEBAR
       ======================================================== */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e8edf3;
    }

    section[data-testid="stSidebar"] > div {
        padding-top: 25px;
    }

    .brand {
        padding: 4px 12px 26px 12px;
    }

    .brand-row {
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .brand-icon {
        width: 38px;
        height: 38px;
        border-radius: 11px;
        background: linear-gradient(
            135deg,
            #2563eb,
            #4f46e5
        );
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 19px;
        font-weight: 800;
    }

    .brand-name {
        color: #111827;
        font-size: 18px;
        font-weight: 800;
        letter-spacing: -0.4px;
    }

    .brand-subtitle {
        color: #94a3b8;
        font-size: 10px;
        margin-top: 1px;
    }

    .nav-label {
        color: #94a3b8;
        font-size: 10px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 18px 12px 7px;
    }

    .sidebar-info {
        background: #f8fafc;
        border: 1px solid #edf1f5;
        border-radius: 12px;
        padding: 13px;
        margin-top: 18px;
    }

    .sidebar-info-title {
        color: #334155;
        font-size: 11px;
        font-weight: 700;
    }

    .sidebar-info-text {
        color: #94a3b8;
        font-size: 10px;
        line-height: 1.5;
        margin-top: 4px;
    }

    /* ========================================================
       HEADER
       ======================================================== */

    .top-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 26px;
    }

    .eyebrow {
        color: #2563eb;
        font-size: 11px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }

    .page-title {
        color: #111827;
        font-size: 30px;
        line-height: 1.1;
        font-weight: 800;
        letter-spacing: -1px;
    }

    .page-description {
        color: #64748b;
        font-size: 13px;
        margin-top: 7px;
    }

    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 7px;
        background: #ecfdf5;
        border: 1px solid #d1fae5;
        color: #047857;
        border-radius: 999px;
        padding: 7px 12px;
        font-size: 11px;
        font-weight: 700;
    }

    .status-dot {
        width: 7px;
        height: 7px;
        border-radius: 50%;
        background: #10b981;
    }

    /* ========================================================
       KPI CARDS
       ======================================================== */

    .kpi-card {
        background: #ffffff;
        border: 1px solid #e8edf3;
        border-radius: 15px;
        padding: 19px 20px;
        min-height: 128px;
        box-shadow:
            0 1px 2px rgba(15, 23, 42, 0.02);
    }

    .kpi-top {
        display: flex;
        align-items: center;
        justify-content: space-between;
    }

    .kpi-label {
        color: #64748b;
        font-size: 11px;
        font-weight: 600;
    }

    .kpi-icon {
        width: 31px;
        height: 31px;
        border-radius: 9px;
        background: #eff6ff;
        color: #2563eb;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 14px;
    }

    .kpi-value {
        color: #111827;
        font-size: 25px;
        font-weight: 800;
        letter-spacing: -0.6px;
        margin-top: 13px;
    }

    .kpi-caption {
        color: #94a3b8;
        font-size: 10px;
        margin-top: 5px;
    }

    /* ========================================================
       SECTION
       ======================================================== */

    .section-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin: 30px 0 13px;
    }

    .section-title {
        color: #111827;
        font-size: 16px;
        font-weight: 750;
        letter-spacing: -0.2px;
    }

    .section-caption {
        color: #94a3b8;
        font-size: 10px;
    }

    /* ========================================================
       MAIN CARDS
       ======================================================== */

    .panel {
        background: #ffffff;
        border: 1px solid #e8edf3;
        border-radius: 15px;
        padding: 21px;
        box-shadow:
            0 1px 2px rgba(15, 23, 42, 0.02);
    }

    /* ========================================================
       AI DECISION
       ======================================================== */

    .decision-panel {
        background:
            linear-gradient(
                135deg,
                #ffffff 0%,
                #f8fbff 100%
            );
        border: 1px solid #dbeafe;
        border-radius: 15px;
        padding: 22px;
        min-height: 245px;
        position: relative;
        overflow: hidden;
    }

    .decision-panel::after {
        content: "";
        position: absolute;
        width: 150px;
        height: 150px;
        border-radius: 50%;
        background: #eff6ff;
        right: -70px;
        top: -70px;
        opacity: 0.8;
    }

    .decision-badge {
        display: inline-flex;
        align-items: center;
        gap: 6px;
        background: #eff6ff;
        color: #2563eb;
        border-radius: 999px;
        padding: 6px 10px;
        font-size: 10px;
        font-weight: 750;
        position: relative;
        z-index: 1;
    }

    .decision-title {
        color: #111827;
        font-size: 22px;
        font-weight: 800;
        letter-spacing: -0.5px;
        margin-top: 18px;
        position: relative;
        z-index: 1;
    }

    .decision-description {
        color: #475569;
        font-size: 13px;
        line-height: 1.6;
        max-width: 600px;
        margin-top: 8px;
        position: relative;
        z-index: 1;
    }

    .action-label {
        color: #111827;
        font-size: 11px;
        font-weight: 750;
        margin-top: 20px;
        position: relative;
        z-index: 1;
    }

    .action-text {
        color: #64748b;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 4px;
        position: relative;
        z-index: 1;
    }

    /* ========================================================
       HEALTH
       ======================================================== */

    .health-panel {
        background: #ffffff;
        border: 1px solid #e8edf3;
        border-radius: 15px;
        padding: 21px;
        min-height: 245px;
    }

    .health-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .health-label {
        color: #64748b;
        font-size: 11px;
        font-weight: 650;
    }

    .health-tag {
        color: #047857;
        background: #ecfdf5;
        border-radius: 999px;
        padding: 5px 9px;
        font-size: 9px;
        font-weight: 750;
    }

    .health-score-row {
        display: flex;
        align-items: baseline;
        gap: 6px;
        margin-top: 22px;
    }

    .health-score {
        color: #111827;
        font-size: 48px;
        line-height: 1;
        font-weight: 850;
        letter-spacing: -2px;
    }

    .health-max {
        color: #94a3b8;
        font-size: 13px;
    }

    .health-status {
        color: #059669;
        font-size: 12px;
        font-weight: 750;
        margin-top: 7px;
    }

    .health-description {
        color: #94a3b8;
        font-size: 10px;
        line-height: 1.5;
        margin-top: 14px;
    }

    /* ========================================================
       ACTIVITY
       ======================================================== */

    .activity-panel {
        background: #ffffff;
        border: 1px solid #e8edf3;
        border-radius: 15px;
        padding: 19px 21px;
    }

    .activity-row {
        display: flex;
        gap: 12px;
        position: relative;
        padding: 9px 0;
    }

    .activity-row:not(:last-child)::before {
        content: "";
        position: absolute;
        left: 6px;
        top: 25px;
        bottom: -4px;
        width: 1px;
        background: #e2e8f0;
    }

    .activity-icon {
        width: 13px;
        height: 13px;
        min-width: 13px;
        border-radius: 50%;
        background: #ecfdf5;
        border: 2px solid #34d399;
        margin-top: 2px;
        z-index: 2;
    }

    .activity-name {
        color: #334155;
        font-size: 11px;
        font-weight: 700;
    }

    .activity-message {
        color: #94a3b8;
        font-size: 10px;
        margin-top: 3px;
    }

    /* ========================================================
       RISK / OPPORTUNITY
       ======================================================== */

    .insight-item {
        border-bottom: 1px solid #f1f5f9;
        padding: 13px 0;
    }

    .insight-item:last-child {
        border-bottom: none;
    }

    .insight-title {
        color: #334155;
        font-size: 12px;
        font-weight: 700;
    }

    .insight-text {
        color: #64748b;
        font-size: 10px;
        line-height: 1.5;
        margin-top: 4px;
    }

    .risk-badge {
        display: inline-block;
        color: #dc2626;
        background: #fef2f2;
        border-radius: 999px;
        padding: 3px 7px;
        font-size: 8px;
        font-weight: 750;
        margin-left: 5px;
    }

    .opportunity-badge {
        display: inline-block;
        color: #047857;
        background: #ecfdf5;
        border-radius: 999px;
        padding: 3px 7px;
        font-size: 8px;
        font-weight: 750;
        margin-left: 5px;
    }

    /* ========================================================
       EMPTY STATE
       ======================================================== */

    .empty-panel {
        background: #ffffff;
        border: 1px solid #e8edf3;
        border-radius: 18px;
        padding: 70px 30px;
        text-align: center;
        margin-top: 20px;
    }

    .empty-icon {
        font-size: 45px;
        margin-bottom: 12px;
    }

    .empty-title {
        color: #111827;
        font-size: 22px;
        font-weight: 800;
    }

    .empty-text {
        color: #64748b;
        font-size: 12px;
        margin-top: 7px;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            <div class="brand-row">
                <div class="brand-icon">F</div>
                <div>
                    <div class="brand-name">FinTrack AI</div>
                    <div class="brand-subtitle">
                        Agentic Financial Intelligence
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nav-label">Workspace</div>',
        unsafe_allow_html=True,
    )

# Overview is app.py itself.
# Do not use st.page_link("app.py") because the main entrypoint
# cannot be referenced this way.

    st.page_link(
    "pages/1_🤖_Agent_Center.py",
    label="Agent Center",
    icon="🤖",
    )

    st.page_link(
        "pages/2_📊_Analytics.py",
        label="Analytics",
        icon="📊",
    )

    st.page_link(
        "pages/3_⚠️_Risks_&_Opportunities.py",
        label="Risks & Opportunities",
        icon="⚠️",
    )

    st.markdown(
        '<div class="nav-label">AI</div>',
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/4_💬_AI_Copilot.py",
        label="Financial Copilot",
        icon="💬",
    )

    st.markdown(
        '<div class="nav-label">Data</div>',
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/5_📁_Transactions.py",
        label="Transactions",
        icon="📁",
    )

    st.markdown(
        '<div class="nav-label">System</div>',
        unsafe_allow_html=True,
    )

    st.page_link(
        "pages/6_⚙️_Settings.py",
        label="Settings",
        icon="⚙️",
    )

    st.markdown(
        """
        <div class="sidebar-info">
            <div class="sidebar-info-title">
                AI Engine
            </div>
            <div class="sidebar-info-text">
                Multi-agent financial reasoning with
                risk, opportunity, decision and critic agents.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("")

    st.markdown(
        '<div class="nav-label">Upload Data</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Transaction CSV",
        type=["csv"],
        label_visibility="collapsed",
    )

    hf_token = st.text_input(
        "Hugging Face Token",
        type="password",
        value=os.environ.get("HF_TOKEN", ""),
        placeholder="HF token (optional)",
    )

    use_llm = st.checkbox(
        "Use AI categorization",
        value=True,
    )

    analyze = st.button(
        "Analyze Financials",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# HF TOKEN
# ============================================================

if hf_token:
    os.environ["HF_TOKEN"] = hf_token


# ============================================================
# ANALYZE
# ============================================================

if analyze:

    if uploaded_file is None:

        st.error(
            "Upload a transaction CSV before starting the analysis."
        )

    else:

        with st.spinner(
            "FinTrack AI agents are analyzing your financial data..."
        ):

            try:

                state = run_financial_analysis(
                    uploaded_file,
                    use_llm=use_llm,
                )

                save_financial_state(state)

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Analysis failed: {exc}"
                )


# ============================================================
# EMPTY STATE
# ============================================================

if not has_financial_state():

    st.markdown(
        """
        <div class="top-header">

            <div>
                <div class="eyebrow">
                    FINANCIAL INTELLIGENCE
                </div>

                <div class="page-title">
                    Business Overview
                </div>

                <div class="page-description">
                    Understand your financial performance with
                    autonomous AI analysis.
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="empty-panel">

            <div class="empty-icon">
                📊
            </div>

            <div class="empty-title">
                Your financial workspace is ready
            </div>

            <div class="empty-text">
                Upload a transaction CSV from the sidebar to
                start your AI-powered financial analysis.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
# LOAD STATE
# ============================================================

state = get_financial_state()

df = state["df"]
stats = state["stats"]

decisions = state.get(
    "decisions",
    {},
)

risk = state.get(
    "risk",
    {},
)

opportunity = state.get(
    "opportunity",
    {},
)

decision = state.get(
    "decision",
    {},
)

critic = state.get(
    "critic",
    {},
)


# ============================================================
# FINANCIAL VALUES
# ============================================================

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

net_cash_flow = income - expenses

expense_ratio = (
    expenses / income * 100
    if income > 0
    else 0
)

health_score = int(
    decisions.get(
        "health_score",
        0,
    )
)

health_status = decisions.get(
    "status",
    "Unknown",
)


# ============================================================
# DECISION
# ============================================================

decision_title = decision.get(
    "title",
    "",
)

decision_description = decision.get(
    "description",
    "",
)

recommended_action = decision.get(
    "recommended_action",
    "",
)


if not decision_title:

    opportunities = decisions.get(
        "opportunities",
        [],
    )

    if opportunities:

        first = opportunities[0]

        decision_title = first.get(
            "title",
            "Monitor Financial Performance",
        )

        decision_description = first.get(
            "description",
            "",
        )

    else:

        decision_title = (
            "Monitor Financial Performance"
        )

        decision_description = (
            "Continue monitoring cash flow and major spending categories."
        )


if not recommended_action:

    recommendations = decisions.get(
        "recommendations",
        [],
    )

    if recommendations:

        recommended_action = recommendations[0]

    else:

        recommended_action = decision_description


# ============================================================
# HEADER
# ============================================================

st.markdown(
    f"""
    <div class="top-header">

        <div>

            <div class="eyebrow">
                FINANCIAL INTELLIGENCE
            </div>

            <div class="page-title">
                Business Overview
            </div>

            <div class="page-description">
                Your AI agents have analyzed
                {len(df):,} financial transactions.
            </div>

        </div>

        <div class="status-pill">
            <span class="status-dot"></span>
            AI Analysis Complete
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# KPI CARDS
# ============================================================

kpi1, kpi2, kpi3, kpi4 = st.columns(4)


with kpi1:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-top">

                <div class="kpi-label">
                    Revenue
                </div>

                <div class="kpi-icon">
                    $
                </div>

            </div>

            <div class="kpi-value">
                ${income:,.2f}
            </div>

            <div class="kpi-caption">
                Total income analyzed
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with kpi2:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-top">

                <div class="kpi-label">
                    Expenses
                </div>

                <div class="kpi-icon">
                    ↗
                </div>

            </div>

            <div class="kpi-value">
                ${expenses:,.2f}
            </div>

            <div class="kpi-caption">
                Total business spending
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with kpi3:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-top">

                <div class="kpi-label">
                    Net Cash Flow
                </div>

                <div class="kpi-icon">
                    ↑
                </div>

            </div>

            <div class="kpi-value">
                ${net_cash_flow:,.2f}
            </div>

            <div class="kpi-caption">
                Revenue minus expenses
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with kpi4:

    st.markdown(
        f"""
        <div class="kpi-card">

            <div class="kpi-top">

                <div class="kpi-label">
                    Expense Ratio
                </div>

                <div class="kpi-icon">
                    %
                </div>

            </div>

            <div class="kpi-value">
                {expense_ratio:.1f}%
            </div>

            <div class="kpi-caption">
                Expenses relative to revenue
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# DECISION + HEALTH
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            AI Financial Intelligence
        </div>
        <div class="section-caption">
            Generated by the FinTrack agent system
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

decision_col, health_col = st.columns(
    [1.6, 1]
)


# ------------------------------------------------------------
# AI DECISION
# ------------------------------------------------------------

with decision_col:

    st.markdown(
        f"""
        <div class="decision-panel">

            <div class="decision-badge">
                ✦ AI Decision
            </div>

            <div class="decision-title">
                {decision_title}
            </div>

            <div class="decision-description">
                {decision_description}
            </div>

            <div class="action-label">
                Recommended action
            </div>

            <div class="action-text">
                {recommended_action}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ------------------------------------------------------------
# HEALTH
# ------------------------------------------------------------

with health_col:

    health_color = (
        "#059669"
        if health_score >= 80
        else "#d97706"
        if health_score >= 60
        else "#dc2626"
    )

    st.markdown(
        f"""
        <div class="health-panel">

            <div class="health-header">

                <div class="health-label">
                    Financial Health
                </div>

                <div class="health-tag">
                    AI SCORE
                </div>

            </div>

            <div class="health-score-row">

                <div class="health-score">
                    {health_score}
                </div>

                <div class="health-max">
                    / 100
                </div>

            </div>

            <div class="health-status"
                 style="color:{health_color};">
                ● {health_status}
            </div>

            <div class="health-description">
                Based on cash flow, expense ratio,
                spending patterns and detected risks.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# CASH FLOW CHART
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            Cash Flow
        </div>
        <div class="section-caption">
            Monthly revenue vs expenses
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

monthly = stats.get(
    "monthly"
)

if monthly is not None and len(monthly) > 0:

    chart_df = monthly.copy()

    if "income" not in chart_df.columns:
        chart_df["income"] = 0

    if "expense" not in chart_df.columns:
        chart_df["expense"] = 0

    chart_df = chart_df.reset_index()

    month_column = chart_df.columns[0]

    fig = go.Figure()

    fig.add_trace(
        go.Scatter(
            x=chart_df[month_column],
            y=chart_df["income"],
            mode="lines+markers",
            name="Revenue",
            line=dict(
                color="#2563eb",
                width=3,
            ),
            marker=dict(
                size=6,
            ),
        )
    )

    fig.add_trace(
        go.Scatter(
            x=chart_df[month_column],
            y=chart_df["expense"],
            mode="lines+markers",
            name="Expenses",
            line=dict(
                color="#f59e0b",
                width=3,
            ),
            marker=dict(
                size=6,
            ),
        )
    )

    fig.update_layout(
        height=310,
        margin=dict(
            l=10,
            r=10,
            t=15,
            b=10,
        ),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(
            family="Inter, sans-serif",
            color="#64748b",
            size=11,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        xaxis=dict(
            showgrid=False,
            linecolor="#e2e8f0",
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#f1f5f9",
            zeroline=False,
        ),
        hovermode="x unified",
    )

    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False,
        },
    )


# ============================================================
# ACTIVITY + INSIGHTS
# ============================================================

st.markdown(
    """
    <div class="section-header">
        <div class="section-title">
            Agent Intelligence
        </div>
        <div class="section-caption">
            Latest autonomous activity
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

activity_col, insight_col = st.columns(
    [1, 1]
)


# ============================================================
# RECENT AGENT ACTIVITY
# ============================================================

with activity_col:

    st.markdown(
        '<div class="activity-panel">',
        unsafe_allow_html=True,
    )

    risk_count = len(
        risk.get(
            "risks",
            [],
        )
    )

    opportunity_count = len(
        opportunity.get(
            "opportunities",
            [],
        )
    )

    findings = decisions.get(
        "findings",
        [],
    )

    pattern_count = len(
        findings
    )

    critic_verified = critic.get(
        "approved",
        False,
    )

    activities = [
        (
            "Data Agent",
            f"{len(df)} transactions cleaned",
        ),
        (
            "Analytics Agent",
            f"{pattern_count} financial patterns analyzed",
        ),
        (
            "Opportunity Agent",
            f"{opportunity_count} opportunities identified",
        ),
        (
            "Critic Agent",
            (
                "Decision verified"
                if critic_verified
                else "Decision requires review"
            ),
        ),
        (
            "Categorization Agent",
            f"{len(df)} transactions classified",
        ),
        (
            "Risk Agent",
            f"{risk_count} risks detected",
        ),
        (
            "Decision Agent",
            decision_title,
        ),
        (
            "Insight Agent",
            "Financial briefing generated",
        ),
    ]

    for name, message in activities:

        st.markdown(
            f"""
            <div class="activity-row">

                <div class="activity-icon"></div>

                <div>

                    <div class="activity-name">
                        {name}
                    </div>

                    <div class="activity-message">
                        {message}
                    </div>

                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# RISKS + OPPORTUNITIES
# ============================================================

with insight_col:

    st.markdown(
        '<div class="panel">',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div style="
            color:#111827;
            font-size:13px;
            font-weight:750;
            margin-bottom:3px;
        ">
            Risks & Opportunities
        </div>

        <div style="
            color:#94a3b8;
            font-size:10px;
            margin-bottom:8px;
        ">
            Signals detected by strategic agents
        </div>
        """,
        unsafe_allow_html=True,
    )

    risks = risk.get(
        "risks",
        [],
    )

    opportunities = opportunity.get(
        "opportunities",
        [],
    )

    displayed = 0

    for item in risks[:3]:

        title = item.get(
            "title",
            "Financial Risk",
        )

        description = item.get(
            "description",
            "",
        )

        st.markdown(
            f"""
            <div class="insight-item">

                <div class="insight-title">
                    {title}

                    <span class="risk-badge">
                        RISK
                    </span>
                </div>

                <div class="insight-text">
                    {description}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        displayed += 1

    for item in opportunities[:3]:

        title = item.get(
            "title",
            "Opportunity",
        )

        description = item.get(
            "description",
            "",
        )

        st.markdown(
            f"""
            <div class="insight-item">

                <div class="insight-title">
                    {title}

                    <span class="opportunity-badge">
                        OPPORTUNITY
                    </span>
                </div>

                <div class="insight-text">
                    {description}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

        displayed += 1

    if displayed == 0:

        st.markdown(
            """
            <div style="
                color:#94a3b8;
                font-size:11px;
                padding:18px 0;
            ">
                No significant risks or opportunities detected.
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown(
        "</div>",
        unsafe_allow_html=True,
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="
        text-align:center;
        color:#94a3b8;
        font-size:10px;
        margin-top:35px;
        padding-top:18px;
        border-top:1px solid #e8edf3;
    ">
        FinTrack AI · Agentic Financial Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)

