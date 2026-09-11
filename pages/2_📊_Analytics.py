"""
Analytics page — deep dive into the financial data with Plotly charts.
"""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from utils.financial_state import FinancialState, get_financial_state

st.set_page_config(page_title="Analytics — FinTrack AI", page_icon="📊", layout="wide")

CSS = """
<style>
.ft-h1 { font-size:1.9rem; font-weight:800; color:#0f172a; letter-spacing:-.025em; margin:0; }
.ft-sub { color:#475569; font-size:.95rem; margin-top:4px; }
.ft-kpi-label { font-size:.76rem; text-transform:uppercase; letter-spacing:.08em;
    color:#94a3b8; font-weight:700; margin:14px 0 8px; }
.ft-card { background:#fff; border:1px solid #e2e8f0; border-radius:16px;
    padding:18px 20px; box-shadow:0 1px 2px rgba(15,23,42,.04),0 4px 16px rgba(15,23,42,.06); }
.ft-mini { font-size:.85rem; color:#334155; }
.ft-mini .v { font-size:1.25rem; font-weight:800; color:#0f172a; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


def _base_layout(fig, height=320, y_prefix=False):
    fig.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        font=dict(family="Inter, sans-serif", color="#334155", size=12),
        margin=dict(l=10, r=10, t=10, b=10), height=height,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=False, linecolor="#e2e8f0"),
        yaxis=dict(showgrid=True, gridcolor="#f1f5f9",
                   tickprefix="$" if y_prefix else "", tickformat=",.0f" if y_prefix else ""),
        hoverlabel=dict(bgcolor="white", bordercolor="#e2e8f0", font_size=12),
    )
    return fig


def main() -> None:
    state: FinancialState = get_financial_state()

    st.markdown('<div class="ft-h1">Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="ft-sub">Revenue, expenses, cash flow, categories, vendors, and recurring costs.</div>',
                unsafe_allow_html=True)
    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if not state.stats or state.df is None:
        st.info("Run an analysis on the Overview page first.")
        return

    s = state.stats
    df = state.df

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="ft-card ft-mini">Revenue<div class="v">${s["total_revenue"]:,.0f}</div></div>',
                    unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="ft-card ft-mini">Expenses<div class="v">${s["total_expenses"]:,.0f}</div></div>',
                    unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="ft-card ft-mini">Net Cash Flow<div class="v">${s["net_cash_flow"]:,.0f}</div></div>',
                    unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="ft-card ft-mini">Expense Ratio<div class="v">{s["expense_ratio"]:.1f}%</div></div>',
                    unsafe_allow_html=True)

    monthly = s["monthly"]

    st.markdown('<div class="ft-kpi-label">Revenue & Expense Trends</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[m["month"] for m in monthly], y=[m["revenue"] for m in monthly],
            mode="lines+markers", fill="tozeroy",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=8, color="#2563eb"),
            fillcolor="rgba(37,99,235,0.08)",
            name="Revenue",
            hovertemplate="%{x}<br>Revenue: $%{y:,.0f}<extra></extra>",
        ))
        _base_layout(fig, y_prefix=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=[m["month"] for m in monthly], y=[m["expenses"] for m in monthly],
            mode="lines+markers", fill="tozeroy",
            line=dict(color="#ef4444", width=3),
            marker=dict(size=8, color="#ef4444"),
            fillcolor="rgba(239,68,68,0.08)",
            name="Expenses",
            hovertemplate="%{x}<br>Expenses: $%{y:,.0f}<extra></extra>",
        ))
        _base_layout(fig, y_prefix=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="ft-kpi-label">Cash Flow & Category Breakdown</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        fig = go.Figure()
        fig.add_bar(
            x=[m["month"] for m in monthly], y=[m["net"] for m in monthly],
            marker_color=["#10b981" if m["net"] >= 0 else "#ef4444" for m in monthly],
            name="Net Cash Flow",
            hovertemplate="%{x}<br>Net: $%{y:,.0f}<extra></extra>",
        )
        _base_layout(fig, y_prefix=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    with col2:
        cat = s.get("category_totals", {})
        if cat:
            colors = ["#2563eb", "#3b82f6", "#60a5fa", "#93c5fd",
                      "#a5b4fc", "#c7d2fe", "#ddd6fe", "#e0e7ff"]
            fig = go.Figure(go.Pie(
                labels=list(cat.keys()), values=list(cat.values()),
                hole=0.55,
                marker=dict(colors=colors[:len(cat)], line=dict(color="white", width=2)),
                textinfo="label+percent",
                textfont=dict(size=11),
                hovertemplate="%{label}<br>$%{value:,.0f}<br>%{percent}<extra></extra>",
            ))
            fig.update_layout(
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(family="Inter, sans-serif", color="#334155", size=12),
                margin=dict(l=10, r=10, t=10, b=10), height=320,
                showlegend=False,
            )
            st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
        else:
            st.info("No expense categories available.")

    st.markdown('<div class="ft-kpi-label">Top Vendors by Spend</div>', unsafe_allow_html=True)
    vendors = s.get("vendor_totals", {})
    if vendors:
        v_items = list(vendors.items())[:10][::-1]
        fig = go.Figure(go.Bar(
            x=[v for _, v in v_items], y=[k for k, _ in v_items],
            orientation="h", marker_color="#3b82f6",
            hovertemplate="%{y}<br>$%{x:,.0f}<extra></extra>",
        ))
        _base_layout(fig, height=340, y_prefix=False)
        fig.update_xaxes(tickprefix="$", tickformat=",.0f")
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})
    else:
        st.info("No vendor data available.")

    st.markdown('<div class="ft-kpi-label">Recurring Expenses & Monthly Comparison</div>', unsafe_allow_html=True)
    col1, col2 = st.columns([1, 1.2])
    with col1:
        rec = s.get("recurring_expenses", [])
        if rec:
            st.markdown('<div class="ft-card">', unsafe_allow_html=True)
            for r in rec[:8]:
                st.markdown(
                    f'<div style="display:flex;justify-content:space-between;padding:8px 0;'
                    f'border-bottom:1px dashed #e2e8f0;font-size:.85rem;">'
                    f'<span style="color:#334155;">{r["description"]}</span>'
                    f'<span style="color:#0f172a;font-weight:700;">${r["avg_amount"]:,.0f} × {r["occurrences"]}</span>'
                    f'</div>',
                    unsafe_allow_html=True,
                )
            st.markdown('</div>', unsafe_allow_html=True)
        else:
            st.info("No recurring expense patterns detected.")

    with col2:
        fig = go.Figure()
        fig.add_bar(x=[m["month"] for m in monthly], y=[m["revenue"] for m in monthly],
                    name="Revenue", marker_color="#93c5fd")
        fig.add_bar(x=[m["month"] for m in monthly], y=[m["expenses"] for m in monthly],
                    name="Expenses", marker_color="#fca5a5")
        fig.add_trace(go.Scatter(
            x=[m["month"] for m in monthly], y=[m["net"] for m in monthly],
            name="Net", mode="lines+markers",
            line=dict(color="#2563eb", width=3),
            marker=dict(size=8, color="#2563eb"),
        ))
        fig.update_layout(barmode="group")
        _base_layout(fig, y_prefix=True)
        st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

    st.markdown('<div class="ft-kpi-label">Transaction Analysis</div>', unsafe_allow_html=True)
    summary = df.groupby("category").agg(
        transactions=("amount", "count"),
        total=("abs_amount", "sum"),
        avg=("abs_amount", "mean"),
    ).reset_index().sort_values("total", ascending=False)
    summary["total"] = summary["total"].map(lambda x: f"${x:,.0f}")
    summary["avg"] = summary["avg"].map(lambda x: f"${x:,.0f}")
    st.dataframe(summary, use_container_width=True, hide_index=True)


main()
