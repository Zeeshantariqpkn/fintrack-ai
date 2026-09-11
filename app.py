import os

import streamlit as st
import plotly.express as px

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
# CSS
# ============================================================

st.markdown(
    """
<style>

    /* ---------- GLOBAL ---------- */

    .stApp {
        background: #f7f9fc;
    }

    .block-container {
        max-width: 1400px;
        padding-top: 2rem;
        padding-bottom: 4rem;
    }

    h1, h2, h3 {
        color: #172033;
        letter-spacing: -0.02em;
    }

    p {
        color: #667085;
    }


    /* ---------- SIDEBAR ---------- */

    section[data-testid="stSidebar"] {
        background: #ffffff;
        border-right: 1px solid #e7ebf2;
    }

    .sidebar-brand {
        font-size: 21px;
        font-weight: 800;
        color: #172033;
        margin-bottom: 2px;
    }

    .sidebar-subtitle {
        font-size: 12px;
        color: #98a2b3;
        margin-bottom: 24px;
    }

    .nav-label {
        font-size: 11px;
        font-weight: 700;
        color: #98a2b3;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-top: 22px;
        margin-bottom: 8px;
    }


    /* ---------- HEADER ---------- */

    .page-eyebrow {
        color: #2563eb;
        font-size: 13px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .page-title {
        font-size: 34px;
        font-weight: 800;
        color: #172033;
        margin-bottom: 4px;
    }

    .page-description {
        color: #667085;
        font-size: 15px;
        margin-bottom: 28px;
    }


    /* ---------- METRICS ---------- */

    .metric-card {
        background: #ffffff;
        border: 1px solid #e7ebf2;
        border-radius: 14px;
        padding: 20px;
        min-height: 132px;
        box-shadow: 0 2px 8px rgba(16, 24, 40, 0.03);
    }

    .metric-label {
        color: #667085;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 10px;
    }

    .metric-value {
        color: #172033;
        font-size: 27px;
        font-weight: 800;
        line-height: 1.2;
    }

    .metric-subtitle {
        color: #98a2b3;
        font-size: 12px;
        margin-top: 8px;
    }


    /* ---------- SECTION ---------- */

    .section-title {
        font-size: 19px;
        font-weight: 750;
        color: #172033;
        margin-top: 30px;
        margin-bottom: 14px;
    }


    /* ---------- DECISION ---------- */

    .decision-card {
        background: #ffffff;
        border: 1px solid #dfe7f5;
        border-left: 5px solid #2563eb;
        border-radius: 14px;
        padding: 23px;
        box-shadow: 0 3px 12px rgba(16, 24, 40, 0.04);
        min-height: 210px;
    }

    .decision-label {
        color: #2563eb;
        font-size: 12px;
        font-weight: 800;
        text-transform: uppercase;
        letter-spacing: 0.07em;
        margin-bottom: 8px;
    }

    .decision-title {
        color: #172033;
        font-size: 22px;
        font-weight: 800;
        margin-bottom: 8px;
    }

    .decision-text {
        color: #667085;
        font-size: 14px;
        line-height: 1.6;
    }


    /* ---------- HEALTH ---------- */

    .health-card {
        background: #ffffff;
        border: 1px solid #e7ebf2;
        border-radius: 14px;
        padding: 23px;
        min-height: 210px;
    }

    .health-score {
        font-size: 48px;
        font-weight: 850;
        color: #172033;
        line-height: 1;
    }

    .health-status {
        color: #16a34a;
        font-size: 14px;
        font-weight: 700;
        margin-top: 8px;
    }


    /* ---------- AGENT ACTIVITY ---------- */

    .agent-card {
        background: #ffffff;
        border: 1px solid #e7ebf2;
        border-radius: 12px;
        padding: 15px 17px;
        margin-bottom: 10px;
    }

    .agent-name {
        color: #172033;
        font-size: 14px;
        font-weight: 700;
    }

    .agent-message {
        color: #667085;
        font-size: 12px;
        margin-top: 4px;
    }

    .agent-dot {
        color: #16a34a;
        font-size: 16px;
        margin-right: 7px;
    }


    /* ---------- EMPTY STATE ---------- */

    .empty-card {
        background: #ffffff;
        border: 1px dashed #cfd7e6;
        border-radius: 16px;
        padding: 55px 30px;
        text-align: center;
        margin-top: 30px;
    }

    .empty-icon {
        font-size: 42px;
        margin-bottom: 12px;
    }

    .empty-title {
        color: #172033;
        font-size: 21px;
        font-weight: 800;
    }

    .empty-text {
        color: #667085;
        font-size: 14px;
        max-width: 600px;
        margin: 8px auto 0;
    }


    /* ---------- FOOTER ---------- */

    .footer {
        border-top: 1px solid #e7ebf2;
        margin-top: 45px;
        padding-top: 18px;
        color: #98a2b3;
        font-size: 12px;
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
        '<div class="sidebar-brand">💰 FinTrack AI</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="sidebar-subtitle">'
        'Agentic Financial Intelligence'
        '</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="nav-label">Analyze</div>',
        unsafe_allow_html=True,
    )

    uploaded_file = st.file_uploader(
        "Upload transaction CSV",
        type=["csv"],
        help=(
            "CSV must contain date, description "
            "and amount columns."
        ),
    )

    st.markdown(
        '<div class="nav-label">AI Configuration</div>',
        unsafe_allow_html=True,
    )

    hf_token = st.text_input(
        "Hugging Face token",
        value=os.environ.get(
            "HF_TOKEN",
            "",
        ),
        type="password",
        help=(
            "Optional. Enables Hugging Face "
            "transaction categorization."
        ),
    )

    if hf_token:
        os.environ["HF_TOKEN"] = hf_token

    use_llm = st.checkbox(
        "Use AI categorization",
        value=True,
    )

    st.markdown("")

    analyze_clicked = st.button(
        "🚀 Analyze Financials",
        use_container_width=True,
        type="primary",
    )

    clear_clicked = st.button(
        "Clear Analysis",
        use_container_width=True,
    )

    st.markdown(
        '<div class="nav-label">Pipeline</div>',
        unsafe_allow_html=True,
    )

    st.caption("Data Agent")
    st.caption("Categorization Agent")
    st.caption("Analytics Agent")
    st.caption("Decision Agent")
    st.caption("Insight Agent")


# ============================================================
# CLEAR STATE
# ============================================================

if clear_clicked:

    for key in [
        "financial_state",
        "analysis_source",
    ]:
        if key in st.session_state:
            del st.session_state[key]

    st.rerun()


# ============================================================
# ANALYSIS
# ============================================================

if analyze_clicked:

    if uploaded_file is None:

        st.warning(
            "Upload a transaction CSV first."
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

                st.session_state[
                    "analysis_source"
                ] = uploaded_file.name

                st.success(
                    "Financial analysis completed."
                )

            except Exception as exc:

                st.error(
                    f"Analysis failed: {exc}"
                )


# ============================================================
# HEADER
# ============================================================

st.markdown(
    '<div class="page-eyebrow">'
    'AGENTIC FINANCIAL INTELLIGENCE'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-title">'
    'Financial Overview'
    '</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-description">'
    'Understand your business performance, '
    'discover financial risks, and let AI '
    'identify the next best action.'
    '</div>',
    unsafe_allow_html=True,
)


# ============================================================
# EMPTY STATE
# ============================================================

if not has_financial_state():

    st.markdown(
        """
        <div class="empty-card">
            <div class="empty-icon">📊</div>
            <div class="empty-title">
                Start your financial analysis
            </div>
            <div class="empty-text">
                Upload a transaction CSV from the sidebar
                and let FinTrack AI's agents analyze your
                financial performance, spending patterns,
                risks and opportunities.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="footer">
            FinTrack AI · Agentic Financial Analytics for SMBs
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
# GET STATE
# ============================================================

state = get_financial_state()

df = state["df"]
stats = state["stats"]
decisions = state["decisions"]
agent_status = state["agent_status"]


# ============================================================
# FINANCIAL METRICS
# ============================================================

income = float(
    stats.get("total_income", 0)
)

expenses = float(
    stats.get("total_expense", 0)
)

net_cash_flow = income - expenses

health_score = int(
    decisions.get(
        "health_score",
        0,
    )
)

status = decisions.get(
    "status",
    "Unknown",
)

expense_ratio = float(
    decisions.get(
        "expense_ratio",
        0,
    )
)

st.markdown(
    '<div class="section-title">'
    'Business Snapshot'
    '</div>',
    unsafe_allow_html=True,
)

metric_col1, metric_col2, metric_col3, metric_col4 = (
    st.columns(4)
)


with metric_col1:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Revenue</div>
            <div class="metric-value">
                ${income:,.0f}
            </div>
            <div class="metric-subtitle">
                Total incoming cash
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with metric_col2:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Expenses</div>
            <div class="metric-value">
                ${expenses:,.0f}
            </div>
            <div class="metric-subtitle">
                Total outgoing cash
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with metric_col3:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Net Cash Flow</div>
            <div class="metric-value">
                ${net_cash_flow:,.0f}
            </div>
            <div class="metric-subtitle">
                Revenue minus expenses
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


with metric_col4:

    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">Financial Health</div>
            <div class="metric-value">
                {health_score}/100
            </div>
            <div class="metric-subtitle">
                {status} · {expense_ratio:.1f}% expense ratio
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# AI DECISION
# ============================================================

st.markdown(
    '<div class="section-title">'
    'What should you do?'
    '</div>',
    unsafe_allow_html=True,
)

decision_col, health_col = st.columns(
    [2, 1],
    gap="large",
)


with decision_col:

    risks = decisions.get(
        "risks",
        [],
    )

    opportunities = decisions.get(
        "opportunities",
        [],
    )

    recommendations = decisions.get(
        "recommendations",
        [],
    )

    if opportunities:

        primary_opportunity = opportunities[0]

        decision_title = primary_opportunity.get(
            "title",
            "Financial Optimization",
        )

        decision_description = primary_opportunity.get(
            "description",
            "",
        )

    elif risks:

        primary_risk = risks[0]

        decision_title = primary_risk.get(
            "title",
            "Financial Risk",
        )

        decision_description = primary_risk.get(
            "description",
            "",
        )

    else:

        decision_title = "Maintain Financial Discipline"

        decision_description = (
            "Your financial position is stable. "
            "Continue monitoring cash flow and "
            "major spending categories."
        )

    st.markdown(
        f"""
        <div class="decision-card">

            <div class="decision-label">
                AI Decision
            </div>

            <div class="decision-title">
                {decision_title}
            </div>

            <div class="decision-text">
                {decision_description}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    if recommendations:

        st.markdown(
            "**Recommended action**"
        )

        st.info(
            recommendations[0]
        )


with health_col:

    st.markdown(
        f"""
        <div class="health-card">

            <div class="decision-label">
                Financial Health
            </div>

            <div class="health-score">
                {health_score}
            </div>

            <div class="health-status">
                ● {status}
            </div>

            <div class="metric-subtitle">
                Based on cash flow, expense ratio,
                spending patterns and detected risks.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# AGENT ACTIVITY
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Recent Agent Activity'
    '</div>',
    unsafe_allow_html=True,
)

agent_col1, agent_col2 = st.columns(2)

agent_items = list(
    agent_status.items()
)

for index, (
    agent_name,
    info,
) in enumerate(agent_items):

    target_col = (
        agent_col1
        if index % 2 == 0
        else agent_col2
    )

    with target_col:

        message = info.get(
            "message",
            "Completed",
        )

        is_complete = (
            info.get("status")
            == "complete"
        )

        icon = "✓" if is_complete else "⚠"

        st.markdown(
            f"""
            <div class="agent-card">

                <span class="agent-dot">
                    {icon}
                </span>

                <span class="agent-name">
                    {agent_name}
                </span>

                <div class="agent-message">
                    {message}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# FINANCIAL TREND
# ============================================================

st.markdown(
    '<div class="section-title">'
    'Financial Trend'
    '</div>',
    unsafe_allow_html=True,
)

monthly = stats.get(
    "monthly"
)

if monthly is not None and not monthly.empty:

    chart_df = monthly.reset_index()

    chart_df = chart_df.rename(
        columns={
            "month": "Month",
            "income": "Revenue",
            "expense": "Expenses",
        }
    )

    available_columns = [
        column
        for column in [
            "Revenue",
            "Expenses",
        ]
        if column in chart_df.columns
    ]

    if available_columns:

        fig = px.line(
            chart_df,
            x="Month",
            y=available_columns,
            markers=True,
            template="plotly_white",
        )

        fig.update_layout(
            height=360,
            margin=dict(
                l=10,
                r=10,
                t=20,
                b=10,
            ),
            legend_title_text="",
            hovermode="x unified",
        )

        st.plotly_chart(
            fig,
            use_container_width=True,
        )


# ============================================================
# QUICK INSIGHTS
# ============================================================

st.markdown(
    '<div class="section-title">'
    'AI Findings'
    '</div>',
    unsafe_allow_html=True,
)

findings = decisions.get(
    "findings",
    [],
)

if findings:

    finding_col1, finding_col2 = st.columns(2)

    for index, finding in enumerate(
        findings[:6]
    ):

        target_col = (
            finding_col1
            if index % 2 == 0
            else finding_col2
        )

        with target_col:

            finding_type = finding.get(
                "type",
                "Insight",
            )

            title = finding.get(
                "title",
                "Financial Finding",
            )

            description = finding.get(
                "description",
                "",
            )

            if finding_type == "Risk":
                icon = "⚠️"
            elif finding_type == "Opportunity":
                icon = "💡"
            elif finding_type == "Positive":
                icon = "✓"
            elif finding_type == "Vendor":
                icon = "🏢"
            elif finding_type == "Pattern":
                icon = "🔎"
            else:
                icon = "📊"

            st.info(
                f"{icon} **{title}**\n\n"
                f"{description}"
            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        FinTrack AI · Agentic Financial Analytics for SMBs
    </div>
    """,
    unsafe_allow_html=True,
)