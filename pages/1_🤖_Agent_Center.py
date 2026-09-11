import streamlit as st

from utils.financial_state import get_financial_state


st.set_page_config(
    page_title="Agent Center | FinTrack AI",
    page_icon="🤖",
    layout="wide",
)


# ============================================================
# STYLE
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
        background: linear-gradient(135deg, #f8fbff 0%, #eef6ff 100%);
        border: 1px solid #dcecff;
        border-radius: 18px;
        padding: 28px 32px;
        margin-bottom: 24px;
    }

    .hero h1 {
        margin: 0;
        color: #0f172a;
        font-size: 34px;
        font-weight: 750;
    }

    .hero p {
        margin: 8px 0 0 0;
        color: #64748b;
        font-size: 15px;
    }

    .agent-card {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 20px;
        min-height: 170px;
        box-shadow: 0 2px 8px rgba(15, 23, 42, 0.04);
    }

    .agent-icon {
        font-size: 25px;
        margin-bottom: 8px;
    }

    .agent-name {
        font-size: 17px;
        font-weight: 700;
        color: #0f172a;
        margin-bottom: 5px;
    }

    .agent-description {
        color: #64748b;
        font-size: 13px;
        line-height: 1.5;
    }

    .status {
        display: inline-block;
        margin-top: 12px;
        padding: 5px 10px;
        border-radius: 999px;
        font-size: 11px;
        font-weight: 700;
    }

    .status-complete {
        background: #ecfdf5;
        color: #047857;
    }

    .status-active {
        background: #eff6ff;
        color: #1d4ed8;
    }

    .status-review {
        background: #fff7ed;
        color: #c2410c;
    }

    .evidence {
        background: #f8fafc;
        border-left: 4px solid #2563eb;
        border-radius: 8px;
        padding: 12px 14px;
        margin: 8px 0;
        color: #334155;
        font-size: 13px;
    }

    .decision-box {
        background: #f8fbff;
        border: 1px solid #bfdbfe;
        border-radius: 16px;
        padding: 22px;
    }

    .decision-title {
        font-size: 22px;
        font-weight: 750;
        color: #0f172a;
    }

    .decision-reason {
        color: #475569;
        line-height: 1.6;
        margin-top: 8px;
    }

    .approved {
        background: #ecfdf5;
        color: #047857;
        border: 1px solid #a7f3d0;
        border-radius: 10px;
        padding: 12px 16px;
        font-weight: 700;
        text-align: center;
    }

    .revise {
        background: #fff7ed;
        color: #c2410c;
        border: 1px solid #fed7aa;
        border-radius: 10px;
        padding: 12px 16px;
        font-weight: 700;
        text-align: center;
    }

    .metric-box {
        background: white;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 18px;
        text-align: center;
    }

    .metric-value {
        font-size: 28px;
        font-weight: 750;
        color: #0f172a;
    }

    .metric-label {
        color: #64748b;
        font-size: 12px;
        margin-top: 3px;
    }

    .flow-node {
        background: white;
        border: 1px solid #dbeafe;
        border-radius: 12px;
        padding: 13px 8px;
        text-align: center;
        font-size: 12px;
        font-weight: 650;
        color: #334155;
    }

    .flow-arrow {
        text-align: center;
        font-size: 20px;
        color: #94a3b8;
        padding-top: 8px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# LOAD STATE
# ============================================================

state = get_financial_state()

if not state:
    st.markdown(
        """
        <div class="hero">
            <h1>🤖 Agent Center</h1>
            <p>
                Run a financial analysis from the Overview page first.
                The Agent Center will then show the complete autonomous
                reasoning pipeline.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.info(
        "No financial analysis is available yet. "
        "Go to Overview, upload a transaction CSV, and click "
        "'Analyze Financials'."
    )

    st.stop()


df = state["df"]
stats = state["stats"]

decisions = state.get("decisions", {})

risk = state.get("risk", {})
opportunity = state.get("opportunity", {})
decision = state.get("decision", {})
critic = state.get("critic", {})

agent_status = state.get("agent_status", {})


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="hero">
        <h1>🤖 Agent Center</h1>
        <p>
            Autonomous financial reasoning pipeline powered by
            specialized AI agents.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# PIPELINE
# ============================================================

st.subheader("Autonomous Agent Pipeline")

flow = [
    ("📥", "Raw Data"),
    ("🧹", "Data Agent"),
    ("🏷️", "Categorization"),
    ("📊", "Analytics"),
    ("⚠️", "Risk Agent"),
    ("💡", "Opportunity"),
    ("🧠", "Decision"),
    ("🔍", "Critic"),
    ("✨", "Insight"),
]

columns = st.columns(len(flow))

for column, (icon, name) in zip(columns, flow):
    with column:
        st.markdown(
            f"""
            <div class="flow-node">
                {icon}<br>
                {name}
            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# AGENT STATUS
# ============================================================

st.markdown("")
st.subheader("Agent Execution")

agent_definitions = [
    (
        "📥",
        "Data Agent",
        "Cleans, validates and normalizes uploaded financial data.",
        "data",
    ),
    (
        "🏷️",
        "Categorization Agent",
        "Classifies transactions into meaningful financial categories.",
        "categorization",
    ),
    (
        "📊",
        "Analytics Agent",
        "Calculates cash flow, spending patterns and financial metrics.",
        "analytics",
    ),
    (
        "⚠️",
        "Risk Agent",
        "Independently identifies financial risks using evidence.",
        "risk",
    ),
    (
        "💡",
        "Opportunity Agent",
        "Searches for savings, optimization and growth opportunities.",
        "opportunity",
    ),
    (
        "🧠",
        "Decision Agent",
        "Combines competing risk and opportunity signals into a decision.",
        "decision",
    ),
    (
        "🔍",
        "Critic Agent",
        "Reviews the decision and checks whether evidence supports it.",
        "critic",
    ),
    (
        "✨",
        "Insight Agent",
        "Converts validated analysis into business-friendly insights.",
        "insight",
    ),
]

for row_start in range(0, len(agent_definitions), 4):
    row = agent_definitions[row_start:row_start + 4]
    cols = st.columns(4)

    for col, (icon, name, description, key) in zip(cols, row):
        with col:
            status_value = agent_status.get(key, "Complete")

            if isinstance(status_value, dict):
                status_text = status_value.get(
                    "status",
                    "Complete",
                )
            else:
                status_text = str(status_value)

            status_lower = status_text.lower()

            if "review" in status_lower:
                status_class = "status-review"
            elif "active" in status_lower:
                status_class = "status-active"
            else:
                status_class = "status-complete"

            st.markdown(
                f"""
                <div class="agent-card">
                    <div class="agent-icon">{icon}</div>
                    <div class="agent-name">{name}</div>
                    <div class="agent-description">
                        {description}
                    </div>
                    <span class="status {status_class}">
                        ● {status_text}
                    </span>
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# STRATEGIC AGENTS
# ============================================================

st.markdown("")
st.subheader("Strategic Reasoning")

risk_col, opportunity_col = st.columns(2)


# ------------------------------------------------------------
# RISK AGENT
# ------------------------------------------------------------

with risk_col:

    risk_score = risk.get("risk_score", 0)
    risk_level = risk.get("risk_level", "Unknown")

    st.markdown("### ⚠️ Risk Agent")

    metric_a, metric_b = st.columns(2)

    with metric_a:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-value">
                    {risk_score}
                </div>
                <div class="metric-label">
                    Risk Score
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with metric_b:
        st.markdown(
            f"""
            <div class="metric-box">
                <div class="metric-value">
                    {risk_level}
                </div>
                <div class="metric-label">
                    Risk Level
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.markdown("")

    risks = risk.get("risks", [])

    if risks:
        for item in risks:
            title = item.get("title", "Risk")
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
                    <small>
                        Severity: <strong>{severity}</strong>
                    </small>
                </div>
                """,
                unsafe_allow_html=True,
            )
    else:
        st.success(
            "No significant financial risks detected."
        )


# ------------------------------------------------------------
# OPPORTUNITY AGENT
# ------------------------------------------------------------

with opportunity_col:

    st.markdown("### 💡 Opportunity Agent")

    opportunities = opportunity.get(
        "opportunities",
        [],
    )

    evidence = opportunity.get(
        "evidence",
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

    if evidence:
        st.markdown("**Supporting Evidence**")

        for item in evidence:
            st.markdown(
                f"""
                <div class="evidence">
                    {item}
                </div>
                """,
                unsafe_allow_html=True,
            )


# ============================================================
# DECISION AGENT
# ============================================================

st.markdown("")
st.subheader("🧠 Strategic Decision")

decision_title = decision.get(
    "title",
    "No strategic decision generated",
)

decision_description = decision.get(
    "description",
    decision.get(
        "reasoning",
        "No reasoning available.",
    ),
)

decision_action = decision.get(
    "recommended_action",
    "",
)

decision_confidence = decision.get(
    "confidence",
    None,
)

st.markdown(
    f"""
    <div class="decision-box">
        <div class="decision-title">
            {decision_title}
        </div>

        <div class="decision-reason">
            {decision_description}
        </div>

        {
            f'<div class="decision-reason"><strong>Recommended Action:</strong> {decision_action}</div>'
            if decision_action
            else ""
        }
    </div>
    """,
    unsafe_allow_html=True,
)

if decision_confidence is not None:

    try:
        confidence_value = float(
            decision_confidence
        )

        if confidence_value <= 1:
            confidence_value *= 100

        confidence_value = max(
            0,
            min(100, confidence_value),
        )

        st.progress(
            confidence_value / 100,
            text=(
                f"Decision confidence: "
                f"{confidence_value:.0f}%"
            ),
        )

    except (
        TypeError,
        ValueError,
    ):
        pass


# ============================================================
# DECISION EVIDENCE
# ============================================================

decision_evidence = decision.get(
    "evidence",
    [],
)

if decision_evidence:

    st.markdown("**Decision Evidence**")

    evidence_columns = st.columns(
        min(3, len(decision_evidence))
    )

    for column, item in zip(
        evidence_columns,
        decision_evidence,
    ):
        with column:
            if isinstance(item, dict):
                label = item.get(
                    "label",
                    item.get(
                        "title",
                        "Evidence",
                    ),
                )

                value = item.get(
                    "value",
                    item.get(
                        "description",
                        "",
                    ),
                )

                st.metric(
                    label,
                    value,
                )
            else:
                st.info(str(item))


# ============================================================
# CRITIC AGENT
# ============================================================

st.markdown("")
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
            ✓ APPROVED — Decision supported by financial evidence
        </div>
        """,
        unsafe_allow_html=True,
    )
else:
    st.markdown(
        """
        <div class="revise">
            ↻ REVISE — Critic identified a weakness in the decision
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
    st.markdown("**Review Reasoning**")
    st.write(critic_reasoning)


critic_evidence = critic.get(
    "evidence",
    [],
)

if critic_evidence:

    st.markdown("**Validation Evidence**")

    for item in critic_evidence:

        if isinstance(item, dict):
            title = item.get(
                "title",
                "Evidence",
            )
            description = item.get(
                "description",
                item.get(
                    "value",
                    "",
                ),
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
            st.markdown(
                f"""
                <div class="evidence">
                    {item}
                </div>
                """,
                unsafe_allow_html=True,
            )


revision_required = critic.get(
    "revision_required",
)

if revision_required:

    st.warning(
        f"Revision required: {revision_required}"
    )


# ============================================================
# EVIDENCE SUMMARY
# ============================================================

st.markdown("")
st.subheader("📌 Evidence Summary")

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

transaction_count = len(df)

m1, m2, m3, m4 = st.columns(4)

with m1:
    st.metric(
        "Transactions",
        f"{transaction_count:,}",
    )

with m2:
    st.metric(
        "Income",
        f"${income:,.2f}",
    )

with m3:
    st.metric(
        "Expenses",
        f"${expense:,.2f}",
    )

with m4:
    st.metric(
        "Expense Ratio",
        f"{expense_ratio:.1f}%",
    )


# ============================================================
# REASONING CHAIN
# ============================================================

st.markdown("")
st.subheader("🔗 Agent Reasoning Chain")

reasoning_steps = [
    (
        "1",
        "Data Agent",
        "Validated and normalized the uploaded financial records.",
    ),
    (
        "2",
        "Categorization Agent",
        "Classified transactions into financial categories.",
    ),
    (
        "3",
        "Analytics Agent",
        "Calculated financial metrics and detected patterns.",
    ),
    (
        "4",
        "Risk Agent",
        "Independently evaluated downside financial signals.",
    ),
    (
        "5",
        "Opportunity Agent",
        "Independently searched for optimization opportunities.",
    ),
    (
        "6",
        "Decision Agent",
        "Compared risk and opportunity signals and selected a strategic action.",
    ),
    (
        "7",
        "Critic Agent",
        "Reviewed whether the decision was supported by evidence.",
    ),
    (
        "8",
        "Insight Agent",
        "Converted validated results into business-facing insights.",
    ),
]

for number, title, description in reasoning_steps:

    left, right = st.columns(
        [0.08, 0.92]
    )

    with left:
        st.markdown(
            f"""
            <div style="
                background:#eff6ff;
                color:#1d4ed8;
                border-radius:50%;
                width:34px;
                height:34px;
                display:flex;
                align-items:center;
                justify-content:center;
                font-weight:700;
            ">
                {number}
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown(
            f"""
            <strong>{title}</strong><br>
            <span style="color:#64748b;font-size:13px;">
                {description}
            </span>
            """,
            unsafe_allow_html=True,
        )

    if number != "8":
        st.markdown(
            "<div style='height:8px'></div>",
            unsafe_allow_html=True,
        )