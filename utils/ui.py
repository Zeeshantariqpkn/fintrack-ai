"""
Shared UI helpers: sidebar rendering + auto-nav hider.
"""
from __future__ import annotations

import streamlit as st

from agents.strategic_agents import hf_available


HIDE_AUTO_NAV_CSS = """
<style>
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] {
    display: none !important;
}
section[data-testid="stSidebar"] nav[aria-label="Page navigation"] {
    display: none !important;
}
[data-testid="stSidebarNavItems"] { display: none !important; }
[data-testid="stSidebarNavSeparator"] { display: none !important; }
</style>
"""


def inject_auto_nav_hider() -> None:
    st.markdown(HIDE_AUTO_NAV_CSS, unsafe_allow_html=True)


def _clear_all_state() -> None:
    from utils.financial_state import reset_financial_state
    from utils.vector_store import reset_vector_store
    reset_financial_state()
    reset_vector_store()
    for k in (
        "analysis_done", "pending_upload_trigger",
        "copilot_history", "show_landing", "copilot_pending",
    ):
        st.session_state.pop(k, None)


def render_sidebar() -> None:
    inject_auto_nav_hider()

    with st.sidebar:
        st.markdown(
            """
            <div class="ft-brand">
                <div class="dot">FT</div>
                <div>
                    <div>FinTrack AI</div>
                    <div class="ft-tagline">AI Financial Intelligence</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown('<div class="ft-divider"></div>', unsafe_allow_html=True)

        st.markdown("**Navigation**")
        st.page_link("app.py", label="Overview", icon="📊")
        st.page_link("pages/1_🤖_Agent_Center.py", label="Agent Center", icon="🤖")
        st.page_link("pages/2_📊_Analytics.py", label="Analytics", icon="📈")
        st.page_link(
            "pages/3_⚠️_Risks_&_Opportunities.py",
            label="Risks & Opportunities",
            icon="⚠️",
        )
        st.page_link("pages/4_💬_AI_Copilot.py", label="AI Copilot", icon="💬")
        st.page_link("pages/5_📁_Transactions.py", label="Transactions", icon="📁")
        st.page_link("pages/6_⚙️_Settings.py", label="Settings", icon="⚙️")

        st.markdown('<div class="ft-divider"></div>', unsafe_allow_html=True)

        st.markdown("**Actions**")
        if st.button("📤 Upload new file", use_container_width=True, key="sb_upload_new"):
            _clear_all_state()
            st.session_state["show_landing"] = True
            st.switch_page("app.py")

        if st.button("🔄 Reset analysis", use_container_width=True, key="sb_reset"):
            _clear_all_state()
            st.session_state["show_landing"] = True
            st.switch_page("app.py")

        st.markdown('<div class="ft-divider"></div>', unsafe_allow_html=True)
        st.markdown(
            '<div class="ft-status"><span class="pulse"></span> AI System Online</div>',
            unsafe_allow_html=True,
        )
        if hf_available():
            st.caption("Groq LLM: connected")
        else:
            st.caption("Groq LLM: fallback mode")
