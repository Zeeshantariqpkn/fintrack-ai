
import os

import streamlit as st

from utils.financial_state import (
    get_financial_state,
    has_financial_state,
    save_financial_state,
    run_financial_analysis,
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

    .block-container {
        max-width: 1400px;
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    /* ---------- General ---------- */

    h1, h2, h3 {
        color: #0f172a;
    }

    .page-title {
        font-size: 32px;
        font-weight: 750;
        color: #0f172a;
        margin-bottom: 3px;
    }

    .page-subtitle {
        color: #64748b;
        font-size: 14px;
        margin-bottom: 25px;
    }

    /* ---------- Metric Cards ---------- */

    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 20px;
        min-height: 120px;
    }

    .metric-label {
        color: #64748b;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 8px;
    }

    .metric-value {
        color: #0f172a;
        font-size: 27px;
        font-weight: 750;
    }

    .metric-subtitle {
        color: #94a3b8;
        font-size: 11px;
        line-height: 1.5;
        margin-top: 7px;
    }

    /* ---------- AI Decision ---------- */

    .decision-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 22px;
        min-height: 205px;
    }

    .decision-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 8px;
    }

    .decision-title {
        color: #0f172a;
        font-size: 21px;
        font-weight: 750;
        margin-bottom: 10px;
    }

    .decision-text {
        color: #475569;
        font-size: 13px;
        line-height: 1.6;
    }

    .recommended-label {
        color: #0f172a;
        font-size: 12px;
        font-weight: 700;
        margin-top: 18px;
        margin-bottom: 4px;
    }

    .recommended-text {
        color: #64748b;
        font-size: 12px;
        line-height: 1.5;
    }

    /* ---------- Health ---------- */

    .health-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 22px;
        min-height: 205px;
    }

    .health-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
        margin-bottom: 6px;
    }

    .health-score {
        color: #0f172a;
        font-size: 42px;
        font-weight: 800;
        line-height: 1.1;
    }

    .health-status {
        color: #16a34a;
        font-size: 13px;
        font-weight: 700;
        margin-top: 6px;
    }

    /* ---------- Activity ---------- */

    .activity-container {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px 20px;
    }

    .activity-row {
        display: flex;
        align-items: flex-start;
        gap: 10px;
        padding: 11px 0;
        border-bottom: 1px solid #f1f5f9;
    }

    .activity-row:last-child {
        border-bottom: none;
    }

    .agent-dot {
        color: #16a34a;
        font-size: 14px;
        font-weight: 700;
        width: 18px;
        flex-shrink: 0;
    }

    .agent-name {
        color: #0f172a;
        font-size: 13px;
        font-weight: 650;
    }

    .agent-message {
        color: #64748b;
        font-size: 11px;
        margin-top: 2px;
    }

    /* ---------- Findings ---------- */

    .finding {
        background: #f8fafc;
        border-radius: 10px;
        padding: 13px 15px;
        margin-bottom: 9px;
    }

    .finding-title {
        color: #0f172a;
        font-size: 13px;
        font-weight: 650;
    }

    .finding-description {
        color: #64748b;
        font-size: 11px;
        margin-top: 3px;
        line-height: 1.5;
    }

    /* ---------- Empty State ---------- */

    .empty-state {
        background: #f8fbff;
        border: 1px solid #dbeafe;
        border-radius: 16px;
        padding: 45px 30px;
        text-align: center;
        margin-top: 30px;
    }

    .empty-title {
        color: #0f172a;
        font-size: 22px;
        font-weight: 750;
    }

    .empty-text {
        color: #64748b;
        font-size: 13px;
        margin-top: 8px;
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
        <div style="
            font-size:22px;
            font-weight:800;
            color:#0f172a;
            margin-bottom:2px;
        ">
            💰 FinTrack AI
        </div>

        <div style="
            color:#64748b;
            font-size:12px;
            margin-bottom:22px;
        ">
            Agentic Financial Intelligence
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("### Financial Data")

    uploaded_file = st.file_uploader(
        "Upload transaction CSV",
        type=["csv"],
        help=(
            "CSV should contain date, description and amount columns."
        ),
    )

    st.markdown("### AI Configuration")

    hf_token = st.text_input(
        "Hugging Face Token",
        type="password",
        value=os.environ.get("HF_TOKEN", ""),
        help="Optional. Enables Hugging Face transaction categorization.",
    )

    use_llm = st.checkbox(
        "Use AI categorization",
        value=True,
    )

    analyze_button = st.button(
        "Analyze Financials",
        type="primary",
        use_container_width=True,
    )


# ============================================================
# SET HF TOKEN
# ============================================================

if hf_token:
    os.environ["HF_TOKEN"] = hf_token


# ============================================================
# RUN ANALYSIS
# ============================================================

if analyze_button:

    if uploaded_file is None:

        st.error(
            "Please upload a transaction CSV first."
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

                st.success(
                    "Financial analysis completed successfully."
                )

                st.rerun()

            except Exception as exc:

                st.error(
                    f"Analysis failed: {exc}"
                )


# ============================================================
# LOAD STATE
# ============================================================

if not has_financial_state():

    st.markdown(
        """
        <div class="page-title">
            Financial Overview
        </div>

        <div class="page-subtitle">
            AI-powered financial intelligence for your business.
        </div>

        <div class="empty-state">

            <div style="font-size:42px;">
                📊
            </div>

            <div class="empty-title">
                No financial analysis yet
            </div>

            <div class="empty-text">
                Upload your transaction CSV from the sidebar
                and click "Analyze Financials".
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


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
    {})


# ============================================================
# FINANCIAL METRICS
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

if income > 0:
    expense_ratio = (
        expenses / income
    ) * 100
else:
    expense_ratio = 100.0


# ============================================================
# HEALTH SCORE
# ============================================================

health_score = decisions.get(
    "health_score",
    0,
)

health_status = decisions.get(
    "status",
    "Unknown",
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="page-title">
        Financial Overview
    </div>

    <div class="page-subtitle">
        AI-powered financial intelligence and autonomous decision support.
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# TOP METRICS
# ============================================================

col1, col2, col3, col4 = st.columns(4)


with col1:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Revenue
            </div>

            <div class="metric-value">
                ${income:,.2f}
            </div>

            <div class="metric-subtitle">
                Total business income
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with col2:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Expenses
            </div>

            <div class="metric-value">
                ${expenses:,.2f}
            </div>

            <div class="metric-subtitle">
                Total business spending
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with col3:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Net Cash Flow
            </div>

            <div class="metric-value">
                ${net_cash_flow:,.2f}
            </div>

            <div class="metric-subtitle">
                Revenue minus expenses
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


with col4:

    st.markdown(
        f"""
        <div class="metric-card">

            <div class="metric-label">
                Expense Ratio
            </div>

            <div class="metric-value">
                {expense_ratio:.1f}%
            </div>

            <div class="metric-subtitle">
                Expenses as percentage of revenue
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# AI DECISION + FINANCIAL HEALTH
# ============================================================

st.markdown(
    "<div style='height:24px'></div>",
    unsafe_allow_html=True,
)

decision_column, health_column = st.columns(
    [1.35, 1]
)


# ============================================================
# AI DECISION
# ============================================================

with decision_column:

    # Prefer strategic decision from the new agentic system.
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

    # Fallback to legacy decision data.
    if not decision_title:

        opportunities = decisions.get(
            "opportunities",
            [],
        )

        if opportunities:

            first_opportunity = opportunities[0]

            decision_title = first_opportunity.get(
                "title",
                "Monitor Financial Performance",
            )

            decision_description = first_opportunity.get(
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

            recommended_action = (
                decision_description
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

            <div class="recommended-label">
                Recommended action
            </div>

            <div class="recommended-text">
                {recommended_action}
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# FINANCIAL HEALTH
# ============================================================

with health_column:

    st.markdown(
        f"""
        <div class="health-card">

            <div class="health-label">
                Financial Health
            </div>

            <div class="health-score">
                {health_score}
            </div>

            <div class="health-status">
                ● {health_status}
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
# RECENT AGENT ACTIVITY
# ============================================================

st.markdown(
    "<div style='height:24px'></div>",
    unsafe_allow_html=True,
)

st.subheader("Recent Agent Activity")


# Count useful information from the real state.

transaction_count = len(df)

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


activity_items = [
    (
        "Data Agent",
        f"{transaction_count} transactions cleaned",
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
            if critic.get("approved", False)
            else "Decision requires review"
        ),
    ),
    (
        "Categorization Agent",
        f"{transaction_count} transactions classified",
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


st.markdown(
    '<div class="activity-container">',
    unsafe_allow_html=True,
)


for agent_name, message in activity_items:

    st.markdown(
        f"""
        <div class="activity-row">

            <div class="agent-dot">
                ✓
            </div>

            <div>

                <div class="agent-name">
                    {agent_name}
                </div>

                <div class="agent-message">
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
# FINANCIAL SNAPSHOT
# ============================================================

st.markdown(
    "<div style='height:28px'></div>",
    unsafe_allow_html=True,
)

st.subheader("Financial Snapshot")

snapshot_col1, snapshot_col2 = st.columns(2)


# ------------------------------------------------------------
# LARGEST EXPENSE
# ------------------------------------------------------------

with snapshot_col1:

    by_category = stats.get(
        "by_category"
    )

    if (
        by_category is not None
        and len(by_category) > 0
    ):

        largest_category = str(
            by_category.index[0]
        )

        largest_amount = float(
            by_category.iloc[0]
        )

        st.markdown(
            f"""
            <div class="finding">

                <div class="finding-title">
                    Largest Expense Category
                </div>

                <div class="finding-description">
                    {largest_category}
                    — ${largest_amount:,.2f}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.info(
            "No expense category data available."
        )


# ------------------------------------------------------------
# TOP VENDOR
# ------------------------------------------------------------

with snapshot_col2:

    top_vendors = stats.get(
        "top_vendors"
    )

    if (
        top_vendors is not None
        and len(top_vendors) > 0
    ):

        top_vendor = str(
            top_vendors.index[0]
        )

        top_vendor_amount = float(
            top_vendors.iloc[0]
        )

        st.markdown(
            f"""
            <div class="finding">

                <div class="finding-title">
                    Highest-Spend Vendor
                </div>

                <div class="finding-description">
                    {top_vendor}
                    — ${top_vendor_amount:,.2f}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    else:

        st.info(
            "No vendor spending data available."
        )

