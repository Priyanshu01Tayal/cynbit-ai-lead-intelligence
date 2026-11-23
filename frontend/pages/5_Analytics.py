"""
Cynbit AI - Advanced Analytics & Pipeline Insights Page
Visualizes statistical distributions, deal sizes, velocity, and conversion drop-offs via REST API.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from frontend.utils.api_client import api_client, APIClientError
from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar
from frontend.components.charts import create_conversion_funnel, create_priority_donut, LAYOUT_DEFAULTS

st.set_page_config(page_title="Analytics | Cynbit AI", page_icon="📈", layout="wide")
apply_cynbit_theme()
render_sidebar()

st.title("📈 Advanced Pipeline Analytics")
st.markdown("In-depth statistical insights across lead scores, deal sizes, velocity, and conversion drop-offs via REST API.")

# Fetch analytics from backend API
try:
    summary = api_client.get_analytics_summary()
    funnel = api_client.get_conversion_funnel()
    distributions = api_client.get_distributions()
except APIClientError as e:
    st.error(f"⚠️ Unable to load analytics from backend: {e}")
    st.info("💡 If the backend is waking up from idle sleep on Render, please wait a moment and refresh.")
    if st.button("🔄 Retry"):
        st.rerun()
    st.stop()

# 1. Funnel & Score Distribution
col1, col2 = st.columns([1.2, 1.1])

with col1:
    st.subheader("CRM Conversion Funnel Stages")
    st.markdown("Progressive stage volume from initial inbound inquiry to Closed-Won.")
    fig_funnel = create_conversion_funnel(funnel)
    st.plotly_chart(fig_funnel, use_container_width=True)

with col2:
    st.subheader("Lead Score Distribution")
    st.markdown("Density distribution of 0-100 composite scores across all leads.")
    scores = distributions.get("score_distribution", [])
    if scores:
        fig_hist = go.Figure(data=[go.Histogram(
            x=scores,
            nbinsx=15,
            marker_color="#0096C7",
            marker_line=dict(color="#0B132B", width=1.5)
        )])
        fig_hist.update_layout(
            **LAYOUT_DEFAULTS,
            xaxis_title="Qualification Score",
            yaxis_title="Lead Count",
            xaxis=dict(range=[0, 100], showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)")
        )
        st.plotly_chart(fig_hist, use_container_width=True)
    else:
        st.info("No score data available yet.")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# 2. Priority by Category Cross-Tab & Budget Tiers
col3, col4 = st.columns([1.2, 1])

with col3:
    st.subheader("Priority Distribution by Service Category")
    cat_prio = distributions.get("category_priority", {})
    if cat_prio:
        categories = list(cat_prio.keys())
        hot_vals = [cat_prio[c].get("Hot", 0) for c in categories]
        warm_vals = [cat_prio[c].get("Warm", 0) for c in categories]
        cold_vals = [cat_prio[c].get("Cold", 0) for c in categories]
        
        fig_bar = go.Figure()
        fig_bar.add_trace(go.Bar(name="Hot", x=categories, y=hot_vals, marker_color="#EF476F"))
        fig_bar.add_trace(go.Bar(name="Warm", x=categories, y=warm_vals, marker_color="#FFB703"))
        fig_bar.add_trace(go.Bar(name="Cold", x=categories, y=cold_vals, marker_color="#8D99AE"))
        
        fig_bar.update_layout(
            **LAYOUT_DEFAULTS,
            barmode="stack",
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,0.06)"),
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_bar, use_container_width=True)
    else:
        st.info("No category priority data available.")

with col4:
    st.subheader("Budget Tiers")
    tiers = distributions.get("budget_tiers", {})
    if tiers and any(v > 0 for v in tiers.values()):
        fig_pie = go.Figure(data=[go.Pie(
            labels=list(tiers.keys()),
            values=list(tiers.values()),
            marker=dict(colors=["#0077B6", "#00B4D8", "#48CAE4", "#06D6A0"]),
            hole=0.45
        )])
        fig_pie.update_layout(**LAYOUT_DEFAULTS)
        st.plotly_chart(fig_pie, use_container_width=True)
    else:
        st.info("No budget tier distributions recorded.")
