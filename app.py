
import os

import streamlit as st

from utils.data_processing import (
    load_and_clean,
    compute_stats,
)

from agents.categorize import (
    categorize_transactions,
)

from agents.decision import (
    run_decision_agent,
)

from agents.insights import (
    generate_summary,
    answer_question,
)


# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="FinTrack AI",
    page_icon="💰",
    layout="wide",
)


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown(
    """
    <style>

    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 2rem;
        border-radius: 20px;
        background: linear-gradient(
            135deg,
            #ffffff,
            #eef6ff
        );
        border: 1px solid #dbeafe;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        margin-bottom: 0.25rem;
    }

    .hero p {
        font-size: 1.05rem;
        color: #475569;
        margin-bottom: 0;
    }

    .agent-card {
        padding: 1rem;
        border-radius: 14px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        min-height: 150px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    .agent-icon {
        font-size: 1.8rem;
    }

    .agent-title {
        font-weight: 700;
        font-size: 1rem;
        margin-top: 0.35rem;
    }

    .agent-description {
        color: #64748b;
        font-size: 0.85rem;
        margin-top: 0.35rem;
    }

    .agent-status {
        color: #15803d;
        font-weight: 600;
        font-size: 0.8rem;
        margin-top: 0.6rem;
    }

    .decision-box {
        padding: 1.25rem;
        border-radius: 16px;
        background: #f8fafc;
        border: 1px solid #e2e8f0;
    }

    .finding-box {
        padding: 0.9rem;
        border-radius: 12px;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        margin-bottom: 0.7rem;
    }

    .section-label {
        font-size: 0.8rem;
        font-weight: 700;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    </style>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.title("💰 FinTrack AI")

    st.caption(
        "Agentic Financial Analytics "
        "for Small Businesses"
    )

    st.divider()

    st.subheader("🤖 AI Configuration")

    hf_token = st.text_input(
        "Hugging Face Token (optional)",
        type="password",
        help=(
            "Add your Hugging Face token to enable "
            "LLM-powered categorization, insights "
            "and financial chat."
        ),
    )

    if hf_token:
        os.environ["HF_TOKEN"] = hf_token

    st.divider()

    st.subheader("📂 Financial Data")

    use_sample = st.checkbox(
        "Use sample data",
        value=True,
    )

    uploaded_file = None

    if not use_sample:

        uploaded_file = st.file_uploader(
            "Upload bank statement CSV",
            type=["csv"],
        )

    st.divider()

    st.markdown(
        """
        ### Agentic Pipeline

        🔄 Data Agent

        🏷️ Categorization Agent

        📊 Analytics Agent

        🧠 Decision Agent

        🤖 Insight Agent

        💬 Chat Agent
        """
    )


# =========================================================
# DATA SOURCE
# =========================================================

if use_sample:

    file_to_load = os.path.join(
        os.path.dirname(__file__),
        "sample_data",
        "sample_statement.csv",
    )

elif uploaded_file is not None:

    file_to_load = uploaded_file

else:

    st.info(
        "👈 Upload a CSV or enable "
        "'Use sample data' from the sidebar."
    )

    st.stop()


# =========================================================
# HERO
# =========================================================

st.markdown(
    """
    <div class="hero">

        <h1>💰 FinTrack AI</h1>

        <p>
        Agentic financial intelligence for
        small businesses — turning raw financial
        transactions into decisions and actions.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# =========================================================
# AGENTIC AI EXECUTION CENTER
# =========================================================

st.subheader("🤖 Agentic AI Execution Center")

st.caption(
    "Six specialized agents collaborate in sequence "
    "to transform raw financial data into business decisions."
)


# =========================================================
# AGENT 1 — DATA AGENT
# =========================================================

data_status = st.empty()

with data_status:

    with st.spinner(
        "🔄 Data Agent is cleaning raw transactions..."
    ):

        df = load_and_clean(
            file_to_load
        )

data_status.success(
    f"✅ Data Agent complete — "
    f"{len(df)} transactions cleaned"
)


# =========================================================
# AGENT 2 — CATEGORIZATION AGENT
# =========================================================

category_status = st.empty()

with category_status:

    with st.spinner(
        "🏷️ Categorization Agent is classifying transactions..."
    ):

        df = categorize_transactions(
            df
        )

category_status.success(
    "✅ Categorization Agent complete — "
    "transactions classified"
)


# =========================================================
# AGENT 3 — ANALYTICS AGENT
# =========================================================

analytics_status = st.empty()

with analytics_status:

    with st.spinner(
        "📊 Analytics Agent is calculating financial metrics..."
    ):

        stats = compute_stats(
            df
        )

analytics_status.success(
    "✅ Analytics Agent complete — "
    "financial metrics calculated"
)


# =========================================================
# AGENT 4 — DECISION AGENT
# =========================================================

decision_status = st.empty()

with decision_status:

    with st.spinner(
        "🧠 Decision Agent is evaluating risks and opportunities..."
    ):

        decisions = run_decision_agent(
            df,
            stats,
        )

decision_status.success(
    "✅ Decision Agent complete — "
    "risks, opportunities and recommendations generated"
)


# =========================================================
# AGENT 5 — INSIGHT AGENT
# =========================================================

insight_status = st.empty()

with insight_status:

    with st.spinner(
        "🤖 Insight Agent is generating the executive briefing..."
    ):

        summary = generate_summary(
            stats,
            decisions,
        )

insight_status.success(
    "✅ Insight Agent complete — "
    "business briefing generated"
)


# =========================================================
# AGENT PIPELINE VISUALIZATION
# =========================================================

st.markdown("### 🔗 Agent Collaboration Pipeline")

pipeline_cols = st.columns(6)

pipeline_agents = [
    (
        "🔄",
        "Data Agent",
        "Clean",
    ),
    (
        "🏷️",
        "Categorization",
        "Classify",
    ),
    (
        "📊",
        "Analytics",
        "Measure",
    ),
    (
        "🧠",
        "Decision",
        "Decide",
    ),
    (
        "🤖",
        "Insight",
        "Explain",
    ),
    (
        "💬",
        "Chat",
        "Interact",
    ),
]


for column, agent in zip(
    pipeline_cols,
    pipeline_agents,
):

    icon, name, action = agent

    with column:

        st.markdown(
            f"""
            <div class="agent-card">

                <div class="agent-icon">
                    {icon}
                </div>

                <div class="agent-title">
                    {name}
                </div>

                <div class="agent-description">
                    {action} financial information
                </div>

                <div class="agent-status">
                    ● Ready
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


st.divider()


# =========================================================
# CORE FINANCIAL METRICS
# =========================================================

total_income = stats[
    "total_income"
]

total_expense = stats[
    "total_expense"
]

net_cash_flow = (
    total_income
    - total_expense
)

if total_income > 0:

    expense_ratio = (
        total_expense
        / total_income
    ) * 100

else:

    expense_ratio = 0


col1, col2, col3, col4 = st.columns(4)

col1.metric(
    "Total Income",
    f"${total_income:,.2f}",
)

col2.metric(
    "Total Expenses",
    f"${total_expense:,.2f}",
)

col3.metric(
    "Net Cash Flow",
    f"${net_cash_flow:,.2f}",
)

col4.metric(
    "Expense Ratio",
    f"{expense_ratio:.1f}%",
)


# =========================================================
# DECISION AGENT OUTPUT
# =========================================================

st.subheader("🧠 Decision Agent — Business Decision Center")

decision_col1, decision_col2 = st.columns(
    [1, 2]
)


with decision_col1:

    health_score = decisions[
        "health_score"
    ]

    status = decisions[
        "status"
    ]

    st.metric(
        "Financial Health",
        f"{health_score}/100",
    )

    if status == "Healthy":

        st.success(
            f"🟢 {status}"
        )

    elif status == "Moderate Risk":

        st.warning(
            f"🟡 {status}"
        )

    else:

        st.error(
            f"🔴 {status}"
        )


with decision_col2:

    st.markdown(
        '<div class="decision-box">',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="section-label">'
        'Agent Decision Output'
        '</div>',
        unsafe_allow_html=True,
    )

    st.write(
        "The Decision Agent evaluated the "
        "financial metrics and converted them "
        "into business risks, opportunities "
        "and recommended actions."
    )

    st.markdown(
        f"""
**Transactions analyzed:** {decisions["transaction_count"]}

**Net cash flow:** ${decisions["net_cash_flow"]:,.2f}

**Expense ratio:** {decisions["expense_ratio"]:.1f}%

**Decision status:** {decisions["status"]}
        """
    )

    st.markdown(
        '</div>',
        unsafe_allow_html=True,
    )


# =========================================================
# RISKS / OPPORTUNITIES / RECOMMENDATIONS
# =========================================================

risk_col, opportunity_col, recommendation_col = (
    st.columns(3)
)


# -------------------------
# Risks
# -------------------------

with risk_col:

    st.markdown("### ⚠️ Risks")

    risks = decisions[
        "risks"
    ]

    if risks:

        for risk in risks:

            st.markdown(
                f"""
                <div class="finding-box">

                <strong>
                {risk["title"]}
                </strong>

                <br>

                {risk["description"]}

                <br><br>

                <small>
                Severity: {risk["severity"]}
                </small>

                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.success(
            "No major financial risks detected."
        )


# -------------------------
# Opportunities
# -------------------------

with opportunity_col:

    st.markdown("### 💡 Opportunities")

    opportunities = decisions[
        "opportunities"
    ]

    if opportunities:

        for opportunity in opportunities:

            st.markdown(
                f"""
                <div class="finding-box">

                <strong>
                {opportunity["title"]}
                </strong>

                <br>

                {opportunity["description"]}

                </div>
                """,
                unsafe_allow_html=True,
            )

    else:

        st.info(
            "No major opportunities detected."
        )


# -------------------------
# Recommendations
# -------------------------

with recommendation_col:

    st.markdown("### 🎯 Recommended Actions")

    recommendations = decisions[
        "recommendations"
    ]

    for index, recommendation in enumerate(
        recommendations,
        start=1,
    ):

        st.markdown(
            f"""
            **{index}.**
            {recommendation}
            """
        )


# =========================================================
# AGENT FINDINGS
# =========================================================

st.subheader("🔎 Agent Findings")

findings = decisions[
    "findings"
]

for finding in findings:

    finding_type = finding[
        "type"
    ]

    if finding_type == "Risk":

        icon = "⚠️"

    elif finding_type == "Opportunity":

        icon = "💡"

    elif finding_type == "Positive":

        icon = "✅"

    elif finding_type == "Vendor":

        icon = "🏢"

    elif finding_type == "Pattern":

        icon = "🔁"

    else:

        icon = "📊"

    st.markdown(
        f"""
        <div class="finding-box">

        {icon}
        <strong>
        {finding["title"]}
        </strong>

        <br>

        {finding["description"]}

        </div>
        """,
        unsafe_allow_html=True,
    )


# =========================================================
# INSIGHT AGENT
# =========================================================

st.subheader(
    "🤖 Insight Agent — Executive Financial Briefing"
)

st.info(
    summary
)


# =========================================================
# FINANCIAL HEALTH
# =========================================================

st.subheader("❤️ Financial Health")

health_score = decisions[
    "health_score"
]

if health_score >= 80:

    st.success(
        "🟢 Healthy financial position. "
        "Income currently exceeds expenses "
        "with controlled spending."
    )

elif health_score >= 60:

    st.warning(
        "🟡 Moderate financial risk. "
        "Expense growth should be monitored."
    )

else:

    st.error(
        "🔴 High financial risk. "
        "The business should review spending "
        "and cash-flow pressure."
    )


# =========================================================
# FINANCIAL ANALYTICS
# =========================================================

st.subheader("📊 Financial Analytics")

chart_col1, chart_col2 = st.columns(2)


with chart_col1:

    st.markdown(
        "### Spending by Category"
    )

    if (
        stats["by_category"] is not None
        and len(
            stats["by_category"]
        ) > 0
    ):

        st.bar_chart(
            stats["by_category"]
        )

    else:

        st.info(
            "No categorized expenses available."
        )


with chart_col2:

    st.markdown(
        "### Monthly Income vs Expense"
    )

    st.bar_chart(
        stats["monthly"]
    )


# =========================================================
# TOP VENDORS
# =========================================================

st.markdown(
    "### 🏢 Top Vendors / Descriptions by Spend"
)

st.bar_chart(
    stats["top_vendors"]
)


# =========================================================
# RECURRING EXPENSES
# =========================================================

if len(
    stats["recurring"]
) > 0:

    st.subheader(
        "🔁 Recurring Expenses"
    )

    recurring_df = (
        stats["recurring"]
        .rename("Months Seen")
        .reset_index()
    )

    recurring_df = recurring_df.rename(
        columns={
            "description":
            "Vendor / Description"
        }
    )

    st.dataframe(
        recurring_df,
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# PROCESSED TRANSACTIONS
# =========================================================

with st.expander(
    "📄 View Processed Transactions"
):

    st.dataframe(
        df[
            [
                "date",
                "description",
                "amount",
                "type",
                "category",
            ]
        ],
        use_container_width=True,
        hide_index=True,
    )


# =========================================================
# CHAT AGENT
# =========================================================

st.subheader(
    "💬 Chat Agent"
)

st.caption(
    "The Chat Agent can reason over the outputs "
    "of the Analytics and Decision Agents."
)


if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


for role, message in (
    st.session_state.chat_history
):

    with st.chat_message(role):

        st.markdown(message)


question = st.chat_input(
    "Ask: What is our biggest financial risk?"
)


if question:

    st.session_state.chat_history.append(
        (
            "user",
            question,
        )
    )

    with st.chat_message("user"):

        st.markdown(
            question
        )

    with st.chat_message("assistant"):

        with st.spinner(
            "💬 Chat Agent is reasoning over agent outputs..."
        ):

            answer = answer_question(
                stats,
                question,
                decisions,
            )

        st.markdown(
            answer
        )

    st.session_state.chat_history.append(
        (
            "assistant",
            answer,
        )
    )


# =========================================================
# AGENT ARCHITECTURE
# =========================================================

st.divider()

st.subheader(
    "🏗️ FinTrack AI Agent Architecture"
)

st.code(
    """
RAW BANK DATA
      │
      ▼
┌─────────────────────┐
│ 🔄 DATA AGENT       │
│ Clean & normalize   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 🏷️ CATEGORIZATION  │
│ Classify expenses   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 📊 ANALYTICS AGENT  │
│ Calculate metrics   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 🧠 DECISION AGENT   │
│ Risks & actions     │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 🤖 INSIGHT AGENT    │
│ Explain decisions   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ 💬 CHAT AGENT       │
│ User interaction    │
└─────────────────────┘
    """,
    language="text",
)


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.caption(
    "FinTrack AI • Agentic Financial Analytics "
    "for Small Businesses"
)
