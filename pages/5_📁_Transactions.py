"""
Transactions page — searchable, filterable, sortable table.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

from utils.financial_state import FinancialState, get_financial_state

st.set_page_config(page_title="Transactions — FinTrack AI", page_icon="📁", layout="wide")

CSS = """
<style>
.ft-h1 { font-size:1.9rem; font-weight:800; color:#0f172a; letter-spacing:-.025em; margin:0; }
.ft-sub { color:#475569; font-size:.95rem; margin-top:4px; }
.ft-card { background:#fff; border:1px solid #e2e8f0; border-radius:16px;
    padding:18px 20px; box-shadow:0 1px 2px rgba(15,23,42,.04),0 4px 16px rgba(15,23,42,.06); }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def main() -> None:
    state: FinancialState = get_financial_state()

    st.markdown('<div class="ft-h1">Transactions</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-sub">Every cleaned transaction with its assigned category.</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)

    if state.df is None or state.df.empty:
        st.info("Run an analysis on the Overview page first.")
        return

    df = state.df.copy()

    f1, f2, f3, f4 = st.columns([2, 1, 1, 1])
    with f1:
        search = st.text_input("Search description", placeholder="Type to search…")
    with f2:
        cats = ["All"] + sorted(df["category"].unique().tolist())
        cat_filter = st.selectbox("Category", cats)
    with f3:
        type_filter = st.selectbox("Type", ["All", "Income", "Expense"])
    with f4:
        date_range = st.date_input(
            "Date range",
            value=(df["date"].min().date(), df["date"].max().date()),
        )

    filtered = df.copy()
    if search:
        filtered = filtered[filtered["description"].str.contains(search, case=False, na=False)]
    if cat_filter != "All":
        filtered = filtered[filtered["category"] == cat_filter]
    if type_filter != "All":
        filtered = filtered[filtered["type"] == type_filter.lower()]
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start, end = date_range
        filtered = filtered[
            (filtered["date"].dt.date >= start) & (filtered["date"].dt.date <= end)
        ]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="ft-card"><b>{len(filtered)}</b> rows shown</div>', unsafe_allow_html=True)
    with c2:
        inc = filtered[filtered["type"] == "income"]["amount"].sum()
        st.markdown(f'<div class="ft-card">Income <b>${inc:,.0f}</b></div>', unsafe_allow_html=True)
    with c3:
        exp = filtered[filtered["type"] == "expense"]["abs_amount"].sum()
        st.markdown(f'<div class="ft-card">Expenses <b>${exp:,.0f}</b></div>', unsafe_allow_html=True)
    with c4:
        net = inc - exp
        st.markdown(f'<div class="ft-card">Net <b>${net:,.0f}</b></div>', unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    display = filtered[["date", "description", "category", "type", "amount", "category_confidence"]].copy()
    display["date"] = display["date"].dt.strftime("%Y-%m-%d")
    display["amount"] = display["amount"].map(lambda x: f"${x:,.2f}")
    display["category_confidence"] = display["category_confidence"].map(lambda x: f"{x:.0%}")
    display.columns = ["Date", "Description", "Category", "Type", "Amount", "Confidence"]

    st.dataframe(
        display.sort_values("Date", ascending=False),
        use_container_width=True,
        hide_index=True,
        height=460,
    )

    st.markdown("<div style='height:14px'></div>", unsafe_allow_html=True)
    st.markdown("**Category distribution**")
    dist = df["category"].value_counts().reset_index()
    dist.columns = ["Category", "Count"]
    st.dataframe(dist, use_container_width=True, hide_index=True)


main()
