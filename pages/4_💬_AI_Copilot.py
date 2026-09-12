"""
AI Financial Copilot — with optional vector-DB retrieval (mini-RAG).
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from agents.strategic_agents import call_hf, hf_available
from utils.financial_state import FinancialState, get_financial_state
from utils.ui import render_sidebar
from utils.vector_store import (
    build_documents_from_state,
    get_vector_store,
)

st.set_page_config(page_title="AI Copilot — FinTrack AI", page_icon="💬", layout="wide")

CSS = """
<style>
.ft-h1 { font-size:1.9rem; font-weight:800; color:#0f172a; letter-spacing:-.025em; margin:0; }
.ft-sub { color:#475569; font-size:.95rem; margin-top:4px; }
.ft-msg-user { background:linear-gradient(135deg,#2563eb,#3b82f6); color:#fff;
    padding:12px 16px; border-radius:14px 14px 4px 14px; margin:8px 0 8px auto;
    max-width:75%; font-size:.9rem; box-shadow:0 4px 14px rgba(37,99,235,.22); }
.ft-msg-ai { background:#f8fafc; border:1px solid #e2e8f0; color:#334155;
    padding:14px 18px; border-radius:14px 14px 14px 4px; margin:8px auto 8px 0;
    max-width:85%; font-size:.9rem; line-height:1.6; }
.ft-msg-ai .src { color:#94a3b8; font-size:.75rem; margin-top:8px;
    border-top:1px dashed #e2e8f0; padding-top:8px; font-family:ui-monospace,Menlo,monospace; }
.ft-msg-ai .retrieval { color:#1d4ed8; font-size:.75rem; margin-top:6px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)

render_sidebar()

SUGGESTIONS = [
    "Why is my expense ratio high?",
    "What is my biggest financial risk?",
    "Where can I reduce costs?",
    "Which vendor costs me the most?",
    "Is my business financially healthy?",
    "What should I do next month?",
    "Why did the AI recommend this decision?",
]


def _det_qa(question: str, state: FinancialState) -> Dict[str, Any]:
    q = question.lower()
    s = state.stats
    r = state.risk
    o = state.opportunity
    d = state.decision
    c = state.critic
    citations: List[str] = []

    def cite(metric: str) -> str:
        for e in s.get("evidence", []):
            if e["metric"] == metric:
                return e["interpretation"]
        return ""

    if "expense ratio" in q or ("expense" in q and "ratio" in q):
        interp = cite("expense_ratio")
        answer = f"Your expense ratio is {s['expense_ratio']:.1f}%. {interp} "
        if s["expense_ratio"] > 60:
            answer += (
                f"This is elevated. The largest category is {s.get('largest_category','—')} "
                f"at ${s.get('largest_category_value', 0):,.0f}, which is the most likely lever."
            )
        else:
            answer += "This is within a healthy range for most SMBs."
        citations.append(f"expense_ratio={s['expense_ratio']:.1f}%")
        return {"answer": answer, "citations": citations}

    if "risk" in q and ("biggest" in q or "largest" in q or "main" in q or "top" in q or "what is" in q):
        if not r.get("risks"):
            return {"answer": "The Risk Agent found no material risks in your financial data.",
                    "citations": ["risk_score=0"]}
        top = r["risks"][0]
        answer = (
            f"Your biggest financial risk is **{top['title']}** "
            f"(severity: {top['severity']}). {top['description']} "
            f"Overall risk score: {r['risk_score']}/100 ({r['risk_level']})."
        )
        citations.append(top.get("evidence", ""))
        return {"answer": answer, "citations": citations}

    if "reduce" in q and ("cost" in q or "expense" in q or "spend" in q):
        if o.get("opportunities"):
            top = o["opportunities"][0]
            answer = f"The highest-leverage cost reduction is **{top['title']}**: {top['description']}"
            citations.extend(o.get("evidence", [])[:2])
        else:
            answer = "No major cost-reduction opportunities were detected."
        return {"answer": answer, "citations": citations}

    if "vendor" in q or "supplier" in q:
        if s.get("top_vendor"):
            answer = (
                f"Your highest-spend vendor is **{s['top_vendor']}** at "
                f"${s['top_vendor_value']:,.0f}, representing "
                f"{s['top_vendor_share']:.1f}% of total expenses."
            )
            if s["top_vendor_share"] > 25:
                answer += " This is a concentration risk worth addressing."
            citations.append(f"top_vendor={s['top_vendor']}")
        else:
            answer = "No vendor-level data available."
        return {"answer": answer, "citations": citations}

    if "healthy" in q or "health" in q or ("how" in q and "doing" in q):
        score = state.financial_health_score()
        label = state.health_label()
        answer = (
            f"Your financial health score is **{score}/100 — {label}**. "
            f"Revenue is ${s['total_revenue']:,.0f}, expenses are ${s['total_expenses']:,.0f}, "
            f"and net cash flow is ${s['net_cash_flow']:,.0f}. "
        )
        if score >= 80:
            answer += "The business is in a strong position."
        elif score >= 60:
            answer += "The business is stable but has room to improve."
        else:
            answer += "There are meaningful areas to address — see the Risks page."
        citations.append(f"health_score={score}")
        return {"answer": answer, "citations": citations}

    if "next month" in q or "what should i do" in q or "next step" in q:
        actions = d.get("recommended_actions", [])
        answer = f"Recommended next step: **{d.get('title', '—')}**. "
        if actions:
            answer += "Specifically: " + "; ".join(actions) + "."
        answer += f" Expected impact: {d.get('expected_impact', '—')}."
        return {"answer": answer, "citations": [d.get("title", "")]}

    if "why" in q and ("decision" in q or "recommend" in q):
        answer = (
            f"The Decision Agent recommended **{d.get('title', '—')}** because: "
            f"{d.get('reasoning', '')} "
            f"The Critic Agent "
            f"{'approved' if c.get('approved') else 'requested revision on'} this decision. "
            f"{c.get('reasoning', '')}"
        )
        return {"answer": answer, "citations": d.get("evidence", [])}

    if "cash flow" in q or "cashflow" in q:
        answer = (
            f"Your net cash flow is **${s['net_cash_flow']:,.0f}** "
            f"(revenue ${s['total_revenue']:,.0f} − expenses ${s['total_expenses']:,.0f}). "
            f"You had {s['positive_months']} positive and {s['negative_months']} negative "
            f"cash-flow month(s)."
        )
        citations.append(f"net_cash_flow={s['net_cash_flow']:.0f}")
        return {"answer": answer, "citations": citations}

    answer = (
        "I can answer questions about your revenue, expenses, cash flow, expense ratio, "
        "risks, opportunities, vendors, and the AI decision. "
        f"Quick snapshot: revenue ${s['total_revenue']:,.0f}, "
        f"expenses ${s['total_expenses']:,.0f}, "
        f"net ${s['net_cash_flow']:,.0f}, "
        f"risk {r.get('risk_score', 0)}/100."
    )
    return {"answer": answer, "citations": []}


def answer_question(question: str, state: FinancialState) -> Dict[str, Any]:
    det = _det_qa(question, state)
    config = st.session_state.get("config", {})
    use_vector = config.get("use_vector_db", True)
    embed_model = config.get("embedding_model", "sentence-transformers/all-MiniLM-L6-v2")

    retrieved: List[Dict[str, Any]] = []
    if use_vector:
        store = get_vector_store()
        if not store.is_ready() and state.is_complete():
            docs = build_documents_from_state(state)
            store.build(docs, model=embed_model, prefer_hf=hf_available())
        if store.is_ready():
            retrieved = store.search(question, top_k=5, model=embed_model, prefer_hf=hf_available())

    if not hf_available():
        if retrieved:
            det["citations"] = det.get("citations", []) + [
                f"{d['kind']}: {d['text'][:120]}" for d in retrieved[:3]
            ]
        return det

    s = state.stats
    context = {
        "total_revenue": s["total_revenue"],
        "total_expenses": s["total_expenses"],
        "net_cash_flow": s["net_cash_flow"],
        "expense_ratio": s["expense_ratio"],
        "largest_category": s.get("largest_category"),
        "largest_category_value": s.get("largest_category_value"),
        "top_vendor": s.get("top_vendor"),
        "top_vendor_value": s.get("top_vendor_value"),
        "top_vendor_share": s.get("top_vendor_share"),
        "revenue_trend": s.get("revenue_trend"),
        "expense_trend": s.get("expense_trend"),
        "recurring_count": len(s.get("recurring_expenses", [])),
        "risk_score": state.risk.get("risk_score"),
        "risk_level": state.risk.get("risk_level"),
        "risks": [r["title"] for r in state.risk.get("risks", [])],
        "opportunities": [o["title"] for o in state.opportunity.get("opportunities", [])],
        "decision_title": state.decision.get("title"),
        "decision_reasoning": state.decision.get("reasoning"),
        "critic_approved": state.critic.get("approved"),
        "health_score": state.financial_health_score(),
    }

    retrieved_block = ""
    if retrieved:
        retrieved_block = (
            "Retrieved relevant context (from vector database):\n"
            + "\n".join(f"- {d['text']}" for d in retrieved)
            + "\n\n"
        )

    prompt = (
        "You are the AI Financial Copilot in FinTrack AI. Answer the user's question "
        "using ONLY the financial data below. Do not invent numbers. Be concise (max 120 words). "
        "Cite the specific numbers you use.\n\n"
        f"Financial data:\n{json.dumps(context)[:2000]}\n\n"
        f"{retrieved_block}"
        f"User question: {question}\n\nAnswer:"
    )
    text = call_hf(prompt, max_new_tokens=300, temperature=0.3)
    if not text:
        return det

    return {"answer": text.strip(), "citations": det.get("citations", []), "retrieved": retrieved}


def main() -> None:
    state: FinancialState = get_financial_state()

    st.markdown('<div class="ft-h1">AI Financial Copilot</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="ft-sub">Ask questions about your finances. Answers use only your analyzed data.</div>',
        unsafe_allow_html=True,
    )

    config = st.session_state.get("config", {})
    use_vector = config.get("use_vector_db", True)
    store = get_vector_store()

    if use_vector:
        if store.is_ready():
            st.markdown(
                f'<div style="margin-top:8px;"><span style="display:inline-block;padding:4px 10px;'
                f'border-radius:999px;background:rgba(37,99,235,.1);color:#1d4ed8;font-size:.78rem;'
                f'font-weight:700;">◈ Vector DB active · {store.size()} docs · {store.provider}</span></div>',
                unsafe_allow_html=True,
            )
        else:
            st.markdown(
                '<div style="margin-top:8px;"><span style="display:inline-block;padding:4px 10px;'
                'border-radius:999px;background:rgba(245,158,11,.12);color:#b45309;font-size:.78rem;'
                'font-weight:700;">◈ Vector DB will build on first question</span></div>',
                unsafe_allow_html=True,
            )
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if not state.is_complete():
        st.info("Run an analysis on the Overview page first.")
        return

    if "copilot_history" not in st.session_state:
        st.session_state.copilot_history = []

    st.markdown("**Suggested questions**")
    cols = st.columns(3)
    for i, sug in enumerate(SUGGESTIONS):
        with cols[i % 3]:
            if st.button(sug, key=f"sug_{i}", use_container_width=True):
                st.session_state["copilot_pending"] = sug

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    for turn in st.session_state.copilot_history:
        st.markdown(f'<div class="ft-msg-user">{turn["q"]}</div>', unsafe_allow_html=True)
        cites = "".join(f"<div>↳ {c}</div>" for c in turn.get("citations", []) if c)
        retrieved_html = ""
        if turn.get("retrieved"):
            top = turn["retrieved"][0]
            retrieved_html = (
                f'<div class="retrieval">◈ retrieved: {top["kind"]} '
                f'(score {top["score"]:.2f})</div>'
            )
        st.markdown(
            f'<div class="ft-msg-ai">{turn["a"]}'
            + retrieved_html
            + (f'<div class="src">Evidence<br>{cites}</div>' if cites else "")
            + "</div>",
            unsafe_allow_html=True,
        )

    question = st.chat_input("Ask about your finances…")
    if st.session_state.get("copilot_pending"):
        question = st.session_state.pop("copilot_pending")

    if question:
        with st.spinner("Copilot is thinking…"):
            result = answer_question(question, state)
        st.session_state.copilot_history.append({
            "q": question,
            "a": result["answer"],
            "citations": result.get("citations", []),
            "retrieved": result.get("retrieved", []),
        })
        st.rerun()


main()
