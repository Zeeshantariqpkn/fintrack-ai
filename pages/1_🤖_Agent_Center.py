
import streamlit as st

from utils.financial_state import get_financial_state


st.set_page_config(
    page_title="Agent Center | FinTrack AI",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# CSS
# ============================================================

st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 3rem;
        max-width: 1400px;
    }

    .hero {
        background: #f8fbff;
        border: 1px solid #dbeafe;
        border-radius: 16px;
        padding: 26px 30px;
        margin-bottom: 24px;
    }

    .hero h1 {
        margin: 0;
        color: #0f172a;
        font-size: 32px;
        font-weight: 750;
    }

    .hero p {
        margin: 7px 0 0;
        color: #64748b;
        font-size: 14px;
    }

    .agent-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px;
        min-height: 155px;
    }

    .agent-icon {
        font-size: 23px;
        margin-bottom: 8px;
    }

    .agent-name {
        font-size: 16px;
        font-weight: 700;
        color: #0f172a;
    }

    .agent-description {
        color: #64748b;
        font-size: 12px;
        line-height: 1.5;
        margin-top: 5px;
    }

    .status {
        display: inline-block;
        margin-top: 12px;
        padding: 4px 9px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 700;
        background: #ecfdf5;
        color: #047857;
    }

    .flow-node {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 10px;
        padding: 10px 5px;
        text-align: center;
        font-size: 11px;
        font-weight: 600;
        color: #334155;
    }

    .evidence {
        background: #f8fafc;
        border-left: 3px solid #2563eb;
        border-radius: 7px;
        padding: 10px 12px;
        margin: 7px 0;
        color: #334155;
        font-size: 12px;
    }

    .decision-box {
        background: #f8fbff;
        border: 1px solid #bfdbfe;
        border-radius: 14px;
        padding: 20px;
    }

    .decision-title {
        font-size: 20px;
        font-weight: 750;
        color: #0f172a;
    }

    .decision-description {
        color: #475569;
        margin-top: 7px;
        line-height: 1.5;
        font-size: 13px;
    }

    .approved {
        background: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
        border-radius: 9px;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 700;
        text-align: center;
    }

    .revise {
        background: #fff7ed;
        color: #c2410c;
        border: 1px solid #fed7aa;
        border-radius: 9px;
        padding: 10px 14px;
        font-size: 13px;
        font-weight: 700;
        text-align: center;
    }

    .activity {
        display: flex;
        gap: 12px;
        padding: 10px 0;
        border-bottom: 1px solid #f1f5f9;
    }

    .activity-icon {
        color: #16a34a;
        font-weight: 700;
        font-size: 15px;
    }

    .activity-title {
        color: #0f172a;
        font-weight: 600;
        font-size: 13px;
    }

    .activity-description {
        color: #64748b;
        font-size: 11px;
        margin-top: 2px;
    }

    .section-space {
        margin-top: 28px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD FINANCIAL STATE
# ============================================================

state = get_financial_state()

if not state:
    st.markdown(
        """
        <div class="hero">
            <h1>🤖 Agent Center</h1>
            <p>
                Monitor the autonomous financial analysis agents.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "No analysis is available yet. "
        "Go to Overview, upload your CSV, and click "
        "'Analyze Financials'."
    )

    st.stop()


df = state["df"]
stats = state["stats"]

risk = state.get("risk", {})
opportunity = state.get("opportunity", {})
decision = state.get("decision", {})
critic = state.get("critic", {})

agent_status = state.get(
    "agent_status",
    {},
)


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🤖 Agent Center</h1>
        <p>
            Monitor how FinTrack AI analyzes, reasons and validates
            financial decisions.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# AGENT PIPELINE
# ============================================================

st.subheader("Agent Pipeline")

pipeline = [
    ("📥", "Data"),
    ("🏷️", "Categorize"),
    ("📊", "Analytics"),
    ("⚠️", "Risk"),
    ("💡", "Opportunity"),
    ("🧠", "Decision"),
    ("🔍", "Critic"),
    ("✨", "Insight"),
]

columns = st.columns(len(pipeline))

for column, (icon, name) in zip(columns, pipeline):
    with column:
        st.markdown(
            f"""
            <div class="flow-node">
                {icon}<br>{name}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# AGENT EXECUTION
# ============================================================

st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)

st.subheader("Agent Execution")

agents = [
    (
        "📥",
        "Data Agent",
        "Cleans and validates financial transactions.",
        "data",
    ),
    (
        "🏷️",
        "Categorization Agent",
        "Classifies transactions into financial categories.",
        "categorization",
    ),
    (
        "📊",
        "Analytics Agent",
        "Calculates financial metrics and patterns.",
        "analytics",
    ),
    (
        "⚠️",
        "Risk Agent",
        "Identifies financial risks from the data.",
        "risk",
    ),
    (
        "💡",
        "Opportunity Agent",
        "Finds savings and optimization opportunities.",
        "opportunity",
    ),
    (
        "🧠",
        "Decision Agent",
        "Produces a strategic financial decision.",
        "decision",
    ),
    (
        "🔍",
        "Critic Agent",
        "Reviews the decision against the evidence.",
        "critic",
    ),
    (
        "✨",
        "Insight Agent",
        "Generates business-friendly financial insights.",
        "insight",
    ),
]

for start in range(0, len(agents), 4):

    row = agents[start:start + 4]
    columns = st.columns(4)

    for column, (
        icon,
        name,
        description,
        key,
    ) in zip(columns, row):

        with column:

            status = agent_status.get(
                key,
                "Complete",
            )

            if isinstance(status, dict):
                status = status.get(
                    "status",
                    "Complete",
                )

            st.markdown(
                f"""
                <div class="agent-card">
                    <div class="agent-icon">{icon}</div>

                    <div class="agent-name">
                        {name}
                    </div>

                    <div class="agent-description">
                        {description}
                    </div>

                    <span class="status">
                        ✓ {status}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# RISK + OPPORTUNITY
# ============================================================

st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)

st.subheader("Strategic Analysis")

risk_column, opportunity_column = st.columns(2)


# ------------------------------------------------------------
# RISK
# ------------------------------------------------------------

with risk_column:

    st.markdown("### ⚠️ Risk Agent")

    risk_score = risk.get(
        "risk_score",
        0,
    )

    risk_level = risk.get(
        "risk_level",
        "Unknown",
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Risk Score",
            risk_score,
        )

    with col2:
        st.metric(
            "Risk Level",
            risk_level,
        )

    risks = risk.get(
        "risks",
        [],
    )

    if risks:

        for item in risks:

            title = item.get(
                "title",
                "Risk",
            )

            description = item.get(
                "description",
                "",
            )

            severity = item.get(
                "severity",
                "Medium",
            )

            st.markdown(
                f"""
                <div class="evidence">
                    <strong>{title}</strong><br>
                    {description}<br>
                    <small>Severity: {severity}</small>
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.success(
            "No significant financial risks detected."
        )


# ------------------------------------------------------------
# OPPORTUNITY
# ------------------------------------------------------------

with opportunity_column:

    st.markdown("### 💡 Opportunity Agent")

    opportunities = opportunity.get(
        "opportunities",
        [],
    )

    if opportunities:

        for item in opportunities:

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
                <div class="evidence">
                    <strong>{title}</strong><br>
                    {description}
                </div>
                """,
                unsafe_allow_html=True,
            )

    else:
        st.info(
            "No significant opportunities detected."
        )


# ============================================================
# DECISION
# ============================================================

st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)

st.subheader("🧠 Strategic Decision")

decision_title = decision.get(
    "title",
    "No decision generated",
)

decision_description = decision.get(
    "description",
    decision.get(
        "reasoning",
        "No reasoning available.",
    ),
)

recommended_action = decision.get(
    "recommended_action",
    "",
)

st.markdown(
    f"""
    <div class="decision-box">

        <div class="decision-title">
            {decision_title}
        </div>

        <div class="decision-description">
            {decision_description}
        </div>

        {
            f'''
            <div class="decision-description">
                <strong>Recommended Action:</strong>
                {recommended_action}
            </div>
            '''
            if recommended_action
            else ""
        }

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CRITIC
# ============================================================

st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)

st.subheader("🔍 Critic / Review Agent")

critic_verdict = str(
    critic.get(
        "verdict",
        "UNKNOWN",
    )
).upper()

critic_approved = critic.get(
    "approved",
    critic_verdict == "APPROVED",
)

if critic_approved:

    st.markdown(
        """
        <div class="approved">
            ✓ APPROVED — Decision supported by evidence
        </div>
        """,
        unsafe_allow_html=True,
    )

else:

    st.markdown(
        """
        <div class="revise">
            ↻ REVISE — Decision requires further review
        </div>
        """,
        unsafe_allow_html=True,
    )


critic_reasoning = critic.get(
    "reasoning",
    critic.get(
        "description",
        "",
    ),
)

if critic_reasoning:

    st.markdown("**Review reasoning**")

    st.write(
        critic_reasoning
    )


# ============================================================
# RECENT ACTIVITY
# ============================================================

st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)

st.subheader("Recent Activity")

activities = [
    (
        "✓",
        "Data Agent completed",
        f"{len(df)} transactions cleaned",
    ),
    (
        "✓",
        "Categorization Agent completed",
        f"{len(df)} transactions categorized",
    ),
    (
        "✓",
        "Analytics Agent completed",
        "Financial patterns detected",
    ),
    (
        "✓",
        "Risk Agent completed",
        "Risk assessment generated",
    ),
    (
        "✓",
        "Opportunity Agent completed",
        "Optimization opportunities identified",
    ),
    (
        "✓",
        "Decision Agent completed",
        "Strategic decision generated",
    ),
    (
        "✓",
        "Critic Agent completed",
        "Decision reviewed",
    ),
]

for icon, title, description in activities:

    st.markdown(
        f"""
        <div class="activity">

            <div class="activity-icon">
                {icon}
            </div>

            <div>
                <div class="activity-title">
                    {title}
                </div>

                <div class="activity-description">
                    {description}
                </div>
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )


# ============================================================
# EVIDENCE SUMMARY
# ============================================================

st.markdown("<div class='section-space'></div>", unsafe_allow_html=True)

st.subheader("Evidence Summary")

income = float(
    stats.get(
        "total_income",
        0,
    )
)

expense = float(
    stats.get(
        "total_expense",
        0,
    )
)

net_cash_flow = income - expense

expense_ratio = (
    (expense / income) * 100
    if income
    else 0
)

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Transactions",
        f"{len(df):,}",
    )

with col2:
    st.metric(
        "Income",
        f"${income:,.2f}",
    )

with col3:
    st.metric(
        "Expenses",
        f"${expense:,.2f}",
    )

with col4:
    st.metric(
        "Net Cash Flow",
        f"${net_cash_flow:,.2f}",
    )

