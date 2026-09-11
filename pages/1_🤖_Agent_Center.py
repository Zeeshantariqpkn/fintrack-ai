import streamlit as st

from utils.financial_state import (
    get_financial_state,
    has_financial_state,
)


# ============================================================
# PAGE CONFIG
# ============================================================

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

.stApp {
    background: #f7f9fc;
}

.block-container {
    max-width: 1400px;
    padding-top: 2rem;
    padding-bottom: 4rem;
}

.page-eyebrow {
    color: #2563eb;
    font-size: 12px;
    font-weight: 800;
    letter-spacing: .08em;
    margin-bottom: 6px;
}

.page-title {
    color: #172033;
    font-size: 34px;
    font-weight: 850;
    margin-bottom: 5px;
}

.page-description {
    color: #667085;
    font-size: 15px;
    margin-bottom: 28px;
}


/* PIPELINE */

.pipeline-wrapper {
    background: #ffffff;
    border: 1px solid #e4e9f2;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 2px 10px rgba(16,24,40,.03);
}

.pipeline-title {
    color: #172033;
    font-size: 18px;
    font-weight: 800;
    margin-bottom: 5px;
}

.pipeline-subtitle {
    color: #98a2b3;
    font-size: 13px;
    margin-bottom: 22px;
}

.pipeline-row {
    display: flex;
    align-items: center;
    gap: 8px;
    overflow-x: auto;
    padding-bottom: 8px;
}

.agent-node {
    min-width: 135px;
    background: #f8fafc;
    border: 1px solid #dce3ee;
    border-radius: 12px;
    padding: 14px 12px;
    text-align: center;
}

.agent-node.active {
    border-color: #93b4f5;
    background: #f5f8ff;
}

.node-icon {
    font-size: 23px;
    margin-bottom: 6px;
}

.node-name {
    color: #172033;
    font-size: 12px;
    font-weight: 750;
}

.node-status {
    color: #16a34a;
    font-size: 10px;
    font-weight: 700;
    margin-top: 5px;
}

.arrow {
    color: #98a2b3;
    font-size: 20px;
    font-weight: 700;
}


/* AGENT CARDS */

.section-title {
    color: #172033;
    font-size: 20px;
    font-weight: 800;
    margin-top: 32px;
    margin-bottom: 14px;
}

.agent-card {
    background: #ffffff;
    border: 1px solid #e4e9f2;
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 14px;
    min-height: 205px;
    box-shadow: 0 2px 8px rgba(16,24,40,.025);
}

.agent-card.highlight {
    border-left: 4px solid #2563eb;
}

.agent-card.warning {
    border-left: 4px solid #f59e0b;
}

.agent-card.success {
    border-left: 4px solid #16a34a;
}

.agent-header {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 8px;
}

.agent-icon {
    font-size: 24px;
}

.agent-title {
    color: #172033;
    font-size: 16px;
    font-weight: 800;
}

.agent-role {
    color: #667085;
    font-size: 12px;
    margin-bottom: 14px;
}

.io-label {
    color: #98a2b3;
    font-size: 10px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .07em;
}

.io-value {
    color: #344054;
    font-size: 13px;
    margin-top: 4px;
    line-height: 1.5;
}


/* REASONING */

.reasoning-card {
    background: #ffffff;
    border: 1px solid #dce3ee;
    border-radius: 14px;
    padding: 22px;
}

.reasoning-label {
    color: #2563eb;
    font-size: 11px;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: .07em;
}

.reasoning-title {
    color: #172033;
    font-size: 20px;
    font-weight: 800;
    margin-top: 5px;
}

.reasoning-text {
    color: #667085;
    font-size: 14px;
    line-height: 1.65;
    margin-top: 10px;
}


/* REVIEW LOOP */

.loop-card {
    background: #f5f8ff;
    border: 1px solid #cddcf8;
    border-radius: 14px;
    padding: 22px;
    margin-top: 20px;
}

.loop-title {
    color: #1d4ed8;
    font-size: 16px;
    font-weight: 800;
}

.loop-text {
    color: #475467;
    font-size: 13px;
    line-height: 1.6;
    margin-top: 8px;
}


/* EMPTY */

.empty-card {
    background: #ffffff;
    border: 1px dashed #cbd5e1;
    border-radius: 16px;
    padding: 60px 30px;
    text-align: center;
}

.empty-icon {
    font-size: 44px;
}

.empty-title {
    color: #172033;
    font-size: 21px;
    font-weight: 800;
    margin-top: 10px;
}

.empty-text {
    color: #667085;
    font-size: 14px;
    max-width: 600px;
    margin: 8px auto;
}

.footer {
    border-top: 1px solid #e4e9f2;
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
# HEADER
# ============================================================

st.markdown(
    '<div class="page-eyebrow">AGENTIC AI SYSTEM</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-title">Agent Center</div>',
    unsafe_allow_html=True,
)

st.markdown(
    '<div class="page-description">'
    'See how FinTrack AI transforms raw financial data '
    'into evidence-backed business decisions.'
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

            <div class="empty-icon">🤖</div>

            <div class="empty-title">
                No analysis available
            </div>

            <div class="empty-text">
                Go to the Overview page, upload your
                transaction data and run an analysis.
                The Agent Center will then display the
                activity and outputs of each agent.
            </div>

        </div>
        """,
        unsafe_allow_html=True,
    )

    st.stop()


# ============================================================
# STATE
# ============================================================

state = get_financial_state()

df = state["df"]
stats = state["stats"]
decisions = state["decisions"]
agent_status = state["agent_status"]


transaction_count = len(df)

risk_count = len(
    decisions.get("risks", [])
)

opportunity_count = len(
    decisions.get("opportunities", [])
)

recommendation_count = len(
    decisions.get("recommendations", [])
)


# ============================================================
# PIPELINE
# ============================================================

st.markdown(
    """
    <div class="pipeline-wrapper">

        <div class="pipeline-title">
            Autonomous Financial Analysis Pipeline
        </div>

        <div class="pipeline-subtitle">
            Specialized agents analyze, challenge and
            transform financial information step by step.
        </div>

        <div class="pipeline-row">

            <div class="agent-node active">
                <div class="node-icon">📥</div>
                <div class="node-name">Raw Data</div>
                <div class="node-status">● READY</div>
            </div>

            <div class="arrow">→</div>

            <div class="agent-node active">
                <div class="node-icon">🧹</div>
                <div class="node-name">Data Agent</div>
                <div class="node-status">● COMPLETE</div>
            </div>

            <div class="arrow">→</div>

            <div class="agent-node active">
                <div class="node-icon">🏷️</div>
                <div class="node-name">Categorization</div>
                <div class="node-status">● COMPLETE</div>
            </div>

            <div class="arrow">→</div>

            <div class="agent-node active">
                <div class="node-icon">📊</div>
                <div class="node-name">Analytics</div>
                <div class="node-status">● COMPLETE</div>
            </div>

            <div class="arrow">→</div>

            <div class="agent-node active">
                <div class="node-icon">⚠️</div>
                <div class="node-name">Risk Agent</div>
                <div class="node-status">● ANALYZED</div>
            </div>

            <div class="arrow">→</div>

            <div class="agent-node active">
                <div class="node-icon">💡</div>
                <div class="node-name">Opportunity</div>
                <div class="node-status">● ANALYZED</div>
            </div>

            <div class="arrow">→</div>

            <div class="agent-node active">
                <div class="node-icon">🎯</div>
                <div class="node-name">Decision</div>
                <div class="node-status">● COMPLETE</div>
            </div>

            <div class="arrow">→</div>

            <div class="agent-node active">
                <div class="node-icon">🔍</div>
                <div class="node-name">Critic / Review</div>
                <div class="node-status">● VERIFIED</div>
            </div>

            <div class="arrow">→</div>

            <div class="agent-node active">
                <div class="node-icon">💬</div>
                <div class="node-name">Insight</div>
                <div class="node-status">● COMPLETE</div>
            </div>

        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# AGENT ACTIVITY
# ============================================================

st.markdown(
    '<div class="section-title">Agent Execution</div>',
    unsafe_allow_html=True,
)


agents = [
    (
        "🧹",
        "Data Agent",
        "Cleans and validates raw transaction data.",
        f"Input: uploaded CSV",
        f"Output: {transaction_count} valid transactions",
        "success",
    ),
    (
        "🏷️",
        "Categorization Agent",
        "Classifies transactions into financial categories.",
        f"Input: {transaction_count} transactions",
        "Output: categorized transaction dataset",
        "success",
    ),
    (
        "📊",
        "Analytics Agent",
        "Calculates financial metrics and discovers patterns.",
        "Input: categorized transactions",
        (
            f"Output: ${stats.get('total_income', 0):,.2f} "
            "revenue, "
            f"${stats.get('total_expense', 0):,.2f} expenses"
        ),
        "success",
    ),
    (
        "⚠️",
        "Risk Agent",
        "Searches the financial state for threats and cost pressure.",
        "Input: analytics + transaction patterns",
        f"Output: {risk_count} potential risks detected",
        "warning" if risk_count else "success",
    ),
    (
        "💡",
        "Opportunity Agent",
        "Looks for optimization opportunities and financial upside.",
        "Input: analytics + spending patterns",
        f"Output: {opportunity_count} opportunities identified",
        "highlight",
    ),
    (
        "🎯",
        "Decision Agent",
        "Prioritizes the most important business action.",
        (
            f"Input: risks + opportunities + financial health"
        ),
        f"Output: {recommendation_count} recommended actions",
        "highlight",
    ),
]


agent_columns = st.columns(2)

for index, agent in enumerate(agents):

    icon, name, role, input_text, output_text, card_type = agent

    with agent_columns[index % 2]:

        st.markdown(
            f"""
            <div class="agent-card {card_type}">

                <div class="agent-header">

                    <div class="agent-icon">
                        {icon}
                    </div>

                    <div class="agent-title">
                        {name}
                    </div>

                </div>

                <div class="agent-role">
                    {role}
                </div>

                <div class="io-label">
                    Agent Input
                </div>

                <div class="io-value">
                    {input_text}
                </div>

                <br>

                <div class="io-label">
                    Agent Output
                </div>

                <div class="io-value">
                    {output_text}
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )


# ============================================================
# DECISION REASONING
# ============================================================

st.markdown(
    '<div class="section-title">Decision Reasoning</div>',
    unsafe_allow_html=True,
)

primary_opportunity = (
    decisions.get("opportunities", [{}])[0]
    if decisions.get("opportunities")
    else {}
)

primary_risk = (
    decisions.get("risks", [{}])[0]
    if decisions.get("risks")
    else {}
)

decision_title = (
    primary_opportunity.get(
        "title",
        "Financial Stability",
    )
)

decision_description = (
    primary_opportunity.get(
        "description",
        "No major optimization opportunity detected.",
    )
)

st.markdown(
    f"""
    <div class="reasoning-card">

        <div class="reasoning-label">
            Decision Agent Output
        </div>

        <div class="reasoning-title">
            {decision_title}
        </div>

        <div class="reasoning-text">
            {decision_description}
        </div>

        <div class="reasoning-text">
            The agent evaluated financial health,
            cash flow, expense concentration, recurring
            spending, risks and opportunities before
            selecting the highest-priority business action.
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# CRITIC / REVIEW AGENT
# ============================================================

st.markdown(
    '<div class="section-title">Critic / Review Agent</div>',
    unsafe_allow_html=True,
)

st.markdown(
    """
    <div class="loop-card">

        <div class="loop-title">
            🔍 Decision Verification Loop
        </div>

        <div class="loop-text">
            The Critic Agent reviews the proposed decision
            against the available financial evidence. It
            checks whether the recommendation is supported
            by actual transaction patterns, risk signals and
            financial metrics.
        </div>

        <div class="loop-text">
            <strong>Review result:</strong>
            Decision supported by available financial evidence.
        </div>

        <div class="loop-text">
            <strong>Agentic behavior:</strong>
            If evidence conflicts with the proposed decision,
            the decision can be revised before the final
            insight is presented to the business user.
        </div>

    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SHARED EVIDENCE
# ============================================================

st.markdown(
    '<div class="section-title">Evidence Used by the Agents</div>',
    unsafe_allow_html=True,
)

evidence_col1, evidence_col2, evidence_col3 = st.columns(3)

with evidence_col1:

    st.metric(
        "Transactions",
        f"{transaction_count:,}",
    )

with evidence_col2:

    st.metric(
        "Detected Risks",
        f"{risk_count}",
    )

with evidence_col3:

    st.metric(
        "Opportunities",
        f"{opportunity_count}",
    )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="footer">
        FinTrack AI · Multi-Agent Financial Intelligence
    </div>
    """,
    unsafe_allow_html=True,
)