"""
Cynbit AI - Executive Dashboard Page
Displays real-time pipeline KPIs, priority distributions, and conversion funnel via REST API.
"""

import streamlit as st
import pandas as pd
from frontend.utils.api_client import api_client, APIClientError
from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar
from frontend.components.cards import render_kpi_card, render_priority_badge, render_score_badge
from frontend.components.charts import create_priority_donut, create_category_bar, create_conversion_funnel

st.set_page_config(page_title="Dashboard | Cynbit AI", page_icon="📊", layout="wide")
apply_cynbit_theme()
render_sidebar()

st.title("📊 Executive Lead Dashboard")
st.markdown("Real-time pipeline intelligence, automated qualification metrics, and lead prioritization.")

# Fetch data via centralized API client
try:
    summary = api_client.get_analytics_summary()
    funnel = api_client.get_conversion_funnel()
    recent_leads = api_client.list_leads(limit=6, sort_by="created_at", order="desc")
except APIClientError as e:
    st.error(f"⚠️ Unable to load dashboard analytics from backend: {e}")
    st.info(
        "💡 **Cold Start Notice**: If the backend is hosted on a free cloud tier (Render), "
        "it spins down during periods of inactivity and takes approximately 30–50 seconds to boot up. "
        "Please wait a few seconds and click retry."
    )
    if st.button("🔄 Retry Connection", use_container_width=False):
        st.rerun()
    st.stop()

# 1. Top KPI Row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_kpi_card("Total Inquiries", f"{summary.get('total_leads', 0):,}", "All CRM records", "#3A86FF")
with col2:
    total = max(1, summary.get("total_leads", 0))
    hot = summary.get("hot_leads", 0)
    render_kpi_card("Hot Opportunities", f"{hot:,}", f"{(hot/total*100):.1f}% of pipeline", "#EF476F")
with col3:
    render_kpi_card("Warm Leads", f"{summary.get('warm_leads', 0):,}", "Active nurture pipeline", "#FFB703")
with col4:
    render_kpi_card("Average Score", f"{summary.get('avg_score', 0.0):.1f}", "Target benchmark: 65+", "#00B4D8")
with col5:
    render_kpi_card("Pipeline Value", f"${summary.get('pipeline_value_estimated', 0.0):,.0f}", f"{summary.get('conversion_rate', 0.0)}% Win Rate", "#06D6A0")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# 2. Charts Row
col_c1, col_c2, col_c3 = st.columns([1, 1.2, 1.3])

with col_c1:
    st.subheader("Priority Distribution")
    fig_priority = create_priority_donut(summary.get("priority_counts", {}))
    st.plotly_chart(fig_priority, use_container_width=True)

with col_c2:
    st.subheader("Demand by Service")
    fig_category = create_category_bar(summary.get("category_counts", {}))
    st.plotly_chart(fig_category, use_container_width=True)

with col_c3:
    st.subheader("Conversion Funnel")
    fig_funnel = create_conversion_funnel(funnel)
    st.plotly_chart(fig_funnel, use_container_width=True)

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# 3. Recent Incoming Leads Table
st.subheader("⚡ Recent Qualified Inquiries")

if recent_leads:
    table_data = []
    for l in recent_leads:
        table_data.append({
            "Lead ID": l.get("lead_id", ""),
            "Client / Company": f"{l.get('client_name', '')} ({l.get('client_company', '')})" if l.get("client_company") else l.get("client_name", ""),
            "Service Category": l.get("service_category", ""),
            "Score": l.get("score", 0),
            "Priority": l.get("priority", ""),
            "Est. Budget": l.get("budget_raw", "Unspecified"),
            "Urgency": l.get("urgency_level", "Medium"),
            "Status": l.get("status", "New")
        })
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, use_container_width=True, hide_index=True)
else:
    st.info("No leads recorded yet. Go to 'Add New Lead' to submit a test inquiry.")
