import os
import streamlit as st

from utils.data_processing import load_and_clean, compute_stats
from agents.categorize import categorize_transactions
from agents.insights import generate_summary, answer_question


st.set_page_config(
    page_title="FinTrack AI",
    page_icon="💰",
    layout="wide",
)


# -----------------------------
# Styling
# -----------------------------
st.markdown(
    """
    <style>
    .block-container {
        padding-top: 1.5rem;
        padding-bottom: 3rem;
    }

    .hero {
        padding: 1.8rem;
        border-radius: 18px;
        background: linear-gradient(135deg, #ffffff, #eef6ff);
        border: 1px solid #dbeafe;
        margin-bottom: 1.5rem;
    }

    .hero h1 {
        margin-bottom: 0.25rem;
    }

    .hero p {
        font-size: 1.05rem;
        color: #475569;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:

    st.title("💰 FinTrack AI")

    st.caption(
        "Agentic Financial Analytics for Small Businesses"
    )

    st.divider()

    st.subheader("🤖 AI Configuration")

    hf_token = st.text_input(
        "Hugging Face Token (optional)",
        type="password",
        help=(
            "Add your Hugging Face token to enable "
            "LLM-powered categorization, insights and chat."
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
        ### What FinTrack AI does

        🔹 Cleans financial transactions

        🔹 Categorizes transactions

        🔹 Detects spending patterns

        🔹 Finds recurring expenses

        🔹 Calculates financial health

        🔹 Generates AI insights

        🔹 Answers financial questions
        """
    )


# -----------------------------
# Load Data
# -----------------------------
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


# -----------------------------
# Agent 1: Data Processing
# -----------------------------
with st.spinner(
    "🔄 Data Agent: cleaning transactions..."
):

    df = load_and_clean(file_to_load)


# -----------------------------
# Agent 2: Categorization
# -----------------------------
with st.spinner(
    "🏷️ Categorization Agent: analyzing transactions..."
):

    df = categorize_transactions(df)


# -----------------------------
# Analytics
# -----------------------------
with st.spinner(
    "📊 Analytics Agent: calculating statistics..."
):

    stats = compute_stats(df)


# -----------------------------
# Financial Calculations
# -----------------------------
total_income = stats["total_income"]

total_expense = stats["total_expense"]

net_cash_flow = total_income - total_expense


if total_income > 0:

    expense_ratio = (
        total_expense / total_income
    ) * 100

else:

    expense_ratio = 0


# -----------------------------
# Hero
# -----------------------------
st.markdown(
    """
    <div class="hero">

        <h1>💰 FinTrack AI</h1>

        <p>
        Agentic financial intelligence for small businesses.
        Transform raw financial transactions into
        actionable financial decisions.
        </p>

    </div>
    """,
    unsafe_allow_html=True,
)


# -----------------------------
# KPI Cards
# -----------------------------
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


# -----------------------------
# Financial Health
# -----------------------------
st.subheader("❤️ Financial Health")


if net_cash_flow < 0:

    health_score = 35

elif expense_ratio > 80:

    health_score = 60

elif expense_ratio > 65:

    health_score = 75

else:

    health_score = 90


health_col1, health_col2 = st.columns(
    [1, 3]
)


with health_col1:

    st.metric(
        "Health Score",
        f"{health_score}/100",
    )


with health_col2:

    if health_score >= 80:

        st.success(
            "Healthy financial position. "
            "Income currently exceeds expenses."
        )

    elif health_score >= 60:

        st.warning(
            "Moderate financial risk. "
            "Monitor expense growth carefully."
        )

    else:

        st.error(
            "High financial risk. "
            "Expenses require immediate attention."
        )


# -----------------------------
# AI Financial Analyst
# -----------------------------
st.subheader("🤖 AI Financial Analyst")


with st.spinner(
    "Insight Agent: analyzing financial performance..."
):

    summary = generate_summary(stats)


st.info(summary)


# -----------------------------
# Financial Analytics
# -----------------------------
st.subheader("📊 Financial Analytics")


chart_col1, chart_col2 = st.columns(2)


with chart_col1:

    st.markdown(
        "### Spending by Category"
    )

    if (
        stats["by_category"] is not None
        and len(stats["by_category"]) > 0
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


# -----------------------------
# Top Vendors
# -----------------------------
st.markdown(
    "### 🏢 Top Vendors / Descriptions by Spend"
)

st.bar_chart(
    stats["top_vendors"]
)


# -----------------------------
# Recurring Expenses
# -----------------------------
if len(stats["recurring"]) > 0:

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


# -----------------------------
# Processed Transactions
# -----------------------------
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


# -----------------------------
# Financial Chat
# -----------------------------
st.subheader(
    "💬 Ask FinTrack AI"
)

st.caption(
    "Ask questions about your financial data "
    "using natural language."
)


if "chat_history" not in st.session_state:

    st.session_state.chat_history = []


for role, message in st.session_state.chat_history:

    with st.chat_message(role):

        st.markdown(message)


question = st.chat_input(
    "Example: Which vendor cost us the most?"
)


if question:

    st.session_state.chat_history.append(
        ("user", question)
    )

    with st.chat_message("user"):

        st.markdown(question)

    with st.chat_message("assistant"):

        with st.spinner(
            "Financial AI is thinking..."
        ):

            answer = answer_question(
                stats,
                question,
            )

        st.markdown(answer)

    st.session_state.chat_history.append(
        ("assistant", answer)
    )


# -----------------------------
# Footer
# -----------------------------
st.divider()

st.caption(
    "FinTrack AI • Agentic Financial Analytics "
    "for Small Businesses"
)