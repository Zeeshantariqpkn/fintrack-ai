"""
Settings page.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from agents.strategic_agents import hf_available
from utils.financial_state import (
    FinancialState, get_financial_state, reset_financial_state,
)
from utils.ui import render_sidebar
from utils.vector_store import (
    DEFAULT_EMBEDDING_MODEL, build_documents_from_state,
    get_vector_store, reset_vector_store,
)

st.set_page_config(page_title="Settings — FinTrack AI", page_icon="⚙️", layout="wide")

CSS = """
<style>
.ft-h1 { font-size:1.9rem; font-weight:800; color:#0f172a; letter-spacing:-.025em; margin:0; }
.ft-sub { color:#475569; font-size:.95rem; margin-top:4px; }
.ft-card { background:#fff; border:1px solid #e2e8f0; border-radius:16px;
    padding:20px 22px; box-shadow:0 1px 2px rgba(15,23,42,.04),0 4px 16px rgba(15,23,42,.06); margin-bottom:14px; }
.ft-kpi-label { font-size:.76rem; text-transform:uppercase; letter-spacing:.08em;
    color:#94a3b8; font-weight:700; margin:20px 0 8px; }
.ft-badge-ok { display:inline-block; padding:4px 10px; border-radius:999px;
    background:rgba(16,185,129,.12); color:#047857; font-size:.78rem; font-weight:700; }
.ft-badge-warn { display:inline-block; padding:4px 10px; border-radius:999px;
    background:rgba(245,158,11,.12); color:#b45309; font-size:.78rem; font-weight:700; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

render_sidebar()


def main() -> None:
    st.markdown('<div class="ft-h1">Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-sub">Configure Groq LLM, vector DB, and analysis.</div>',
                unsafe_allow_html=True)

    st.session_state.setdefault("config", {
        "use_ai_categorization": True,
        "use_ai_insights": True,
        "use_vector_db": True,
        "embedding_model": DEFAULT_EMBEDDING_MODEL,
    })
    config = st.session_state.config

    st.markdown('<div class="ft-kpi-label">Groq API</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-card">', unsafe_allow_html=True)

    if hf_available():
        st.markdown('<span class="ft-badge-ok">● GROQ_API_KEY detected</span>',
                    unsafe_allow_html=True)
        st.caption("Model: llama-3.3-70b-versatile · Fast inference · Free tier")
        if st.button("Test Groq connection"):
            import requests as _requests
            key = os.environ.get("GROQ_API_KEY", "")
            if not key:
                try:
                    key = st.secrets.get("GROQ_API_KEY", "")
                except Exception:
                    key = ""
            try:
                r = _requests.post(
                    "https://api.groq.com/openai/v1/chat/completions",
                    headers={"Authorization": f"Bearer {key}"},
                    json={
                        "model": "llama-3.3-70b-versatile",
                        "messages": [{"role": "user", "content": "Say OK."}],
                        "max_tokens": 5,
                    },
                    timeout=15)
                if r.status_code == 200:
                    st.success("Groq connection OK.")
                else:
                    st.error(f"Groq returned HTTP {r.status_code}: {r.text[:200]}")
            except Exception as exc:
                st.error(f"Connection error: {exc}")
    else:
        st.markdown('<span class="ft-badge-warn">● GROQ_API_KEY not configured</span>',
                    unsafe_allow_html=True)
        st.caption("Get a free key at https://console.groq.com/keys")
        st.code('# .streamlit/secrets.toml\nGROQ_API_KEY = "gsk_xxxxxxxxxxxx"', language="toml")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="ft-kpi-label">Vector Database</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-card">', unsafe_allow_html=True)

    config["use_vector_db"] = st.toggle(
        "Enable vector database for the AI Copilot",
        value=config["use_vector_db"])

    config["embedding_model"] = st.text_input(
        "Embedding model",
        value=config["embedding_model"])

    store = get_vector_store()
    stats = store.stats()
    cols = st.columns(3)
    with cols[0]:
        st.metric("Documents", stats["size"])
    with cols[1]:
        st.metric("Provider", stats["provider"])
    with cols[2]:
        st.metric("Dimensions", stats["dim"] or "—")

    state = get_financial_state()

    col_a, col_b = st.columns(2)
    with col_a:
        if st.button("Rebuild vector index", type="primary", use_container_width=True):
            if not state.is_complete():
                st.warning("Run an analysis first.")
            else:
                docs = build_documents_from_state(state)
                store.build(docs, model=config["embedding_model"],
                            prefer_hf=bool(os.environ.get("HF_TOKEN")))
                st.success(f"Indexed {len(docs)} documents using '{store.provider}'.")
    with col_b:
        if st.button("Clear vector index", use_container_width=True):
            reset_vector_store()
            st.success("Vector index cleared.")

    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="ft-kpi-label">Analysis Settings</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-card">', unsafe_allow_html=True)
    config["use_ai_categorization"] = st.toggle(
        "Use AI categorization", value=config["use_ai_categorization"])
    config["use_ai_insights"] = st.toggle(
        "Use AI insight generation", value=config["use_ai_insights"])
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="ft-kpi-label">Data</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-card">', unsafe_allow_html=True)
    if state.df is not None:
        st.caption(f"Current: {len(state.df)} transactions · "
                   f"{state.quality.get('date_range', 'n/a')}")
    else:
        st.caption("No analysis loaded.")
    if st.button("Clear current analysis", type="secondary"):
        reset_financial_state()
        reset_vector_store()
        for k in ("analysis_done", "copilot_history", "show_landing"):
            st.session_state.pop(k, None)
        st.success("Cleared.")
    st.markdown('</div>', unsafe_allow_html=True)


main()
