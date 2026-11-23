"""
Cynbit AI - Executive Dashboard Page
"""

import streamlit as st
import pandas as pd
from app.database import SessionLocal
from app.routes.analytics import get_analytics_summary, get_conversion_funnel
from app.routes.leads import list_leads
from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar
from frontend.components.cards import render_kpi_card, render_priority_badge, render_score_badge
from frontend.components.charts import create_priority_donut, create_category_bar, create_conversion_funnel

st.set_page_config(page_title="Dashboard | Cynbit AI", page_icon="📊", layout="wide")
apply_cynbit_theme()
render_sidebar()

st.title("📊 Executive Lead Dashboard")
st.markdown("Real-time pipeline intelligence, automated qualification metrics, and lead prioritization.")

db = SessionLocal()
try:
    summary = get_analytics_summary(db=db)
    funnel = get_conversion_funnel(db=db)
    recent_leads = list_leads(limit=6, sort_by="created_at", order="desc", db=db)
finally:
    db.close()

# 1. Top KPI Row
col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    render_kpi_card("Total Inquiries", f"{summary['total_leads']:,}", "All CRM records", "#3A86FF")
with col2:
    render_kpi_card("Hot Opportunities", f"{summary['hot_leads']:,}", f"{(summary['hot_leads']/max(1, summary['total_leads'])*100):.1f}% of pipeline", "#EF476F")
with col3:
    render_kpi_card("Warm Leads", f"{summary['warm_leads']:,}", "Active nurture pipeline", "#FFB703")
with col4:
    render_kpi_card("Average Score", f"{summary['avg_score']:.1f}", "Target benchmark: 65+", "#00B4D8")
with col5:
    render_kpi_card("Pipeline Value", f"${summary['pipeline_value_estimated']:,.0f}", f"{summary['conversion_rate']}% Win Rate", "#06D6A0")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# 2. Charts Row
col_c1, col_c2, col_c3 = st.columns([1, 1.2, 1.3])

with col_c1:
    st.subheader("Priority Distribution")
    fig_priority = create_priority_donut(summary["priority_counts"])
    st.plotly_chart(fig_priority, use_container_width=True)

with col_c2:
    st.subheader("Demand by Service")
    fig_category = create_category_bar(summary["category_counts"])
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
            "Lead ID": l["lead_id"],
            "Client / Company": f"{l['client_name']} ({l['client_company']})" if l['client_company'] else l['client_name'],
            "Service Category": l["service_category"],
            "Score": l["score"],
            "Priority": l["priority"],
            "Est. Budget": l["budget_raw"],
            "Urgency": l["urgency_level"],
            "Status": l["status"]
        })
    df_table = pd.DataFrame(table_data)
    st.dataframe(df_table, use_container_width=True, hide_index=True)
else:
    st.info("No leads recorded yet. Go to 'Add New Lead' to submit a test inquiry.")
