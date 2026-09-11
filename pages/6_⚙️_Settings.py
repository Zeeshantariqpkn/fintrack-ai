"""
Settings page — AI configuration, analysis settings, and data reset.
"""
from __future__ import annotations

import os

import streamlit as st

from agents.strategic_agents import hf_available
from utils.financial_state import FinancialState

st.set_page_config(page_title="Settings — FinTrack AI", page_icon="⚙️", layout="wide")

CSS = """
<style>
.ft-h1 { font-size:1.9rem; font-weight:800; color:#0f172a; letter-spacing:-.025em; margin:0; }
.ft-sub { color:#475569; font-size:.95rem; margin-top:4px; }
.ft-card { background:#fff; border:1px solid #e2e8f0; border-radius:16px;
    padding:20px 22px; box-shadow:0 1px 2px rgba(15,23,42,.04),0 4px 16px rgba(15,23,42,.06); margin-bottom:14px; }
.ft-kpi-label { font-size:.76rem; text-transform:uppercase; letter-spacing:.08em;
    color:#94a3b8; font-weight:700; margin-bottom:8px; }
.ft-badge-ok { display:inline-block; padding:4px 10px; border-radius:999px;
    background:rgba(16,185,129,.12); color:#047857; font-size:.78rem; font-weight:700; }
.ft-badge-warn { display:inline-block; padding:4px 10px; border-radius:999px;
    background:rgba(245,158,11,.12); color:#b45309; font-size:.78rem; font-weight:700; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def main() -> None:
    st.markdown('<div class="ft-h1">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-sub">Configure AI behavior and manage your analysis.</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    st.session_state.setdefault("config", {
        "use_ai_categorization": True,
        "use_ai_insights": True,
    })
    config = st.session_state.config

    # -------- AI Configuration --------
    st.markdown('<div class="ft-kpi-label">AI Configuration</div>', unsafe_allow_html=True)
    with st.container():
        st.markdown('<div class="ft-card">', unsafe_allow_html=True)
        if hf_available():
            st.markdown(
                '<span class="ft-badge-ok">● Hugging Face connected</span>',
                unsafe_allow_html=True,
            )
            st.caption("Model: Qwen/Qwen2.5-7B-Instruct")
        else:
            st.markdown(
                '<span class="ft-badge-warn">● Hugging Face not configured</span>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Set the `HF_TOKEN` environment variable (or Streamlit secret) to enable "
                "AI-powered categorization, reasoning, and insight generation. "
                "The app will run in deterministic fallback mode until then."
            )
        st.markdown('</div>', unsafe_allow_html=True)

    # -------- Analysis Settings --------
    st.markdown('<div class="ft-kpi-label">Analysis Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-card">', unsafe_allow_html=True)
    config["use_ai_categorization"] = st.toggle(
        "Use AI categorization",
        value=config["use_ai_categorization"],
        help="When off, the Categorization Agent uses deterministic keyword matching.",
    )
    config["use_ai_insights"] = st.toggle(
        "Use AI insight generation",
        value=config["use_ai_insights"],
        help="When off, the Insight Agent uses the deterministic briefing template.",
    )
    st.markdown('</div>', unsafe_allow_html=True)

    # -------- Data --------
    st.markdown('<div class="ft-kpi-label">Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-card">', unsafe_allow_html=True)
    state: FinancialState = st.session_state.get("fin_state", FinancialState())
    if state.df is not None:
        st.caption(
            f"Current analysis: {len(state.df)} transactions · "
            f"{state.quality.get('date_range', 'n/a')}"
        )
    else:
        st.caption("No analysis loaded.")
    if st.button("Clear current analysis", type="secondary"):
        st.session_state["fin_state"] = FinancialState()
        st.session_state.pop("analysis_done", None)
        st.session_state.pop("copilot_history", None)
        st.success("Analysis cleared. Return to Overview to start a new run.")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="color:#94a3b8;font-size:.78rem;margin-top:12px;">'
        "Your Hugging Face token is never displayed or stored in session state. "
        "Only its availability is checked."
        "</div>",
        unsafe_allow_html=True,
    )


main()
