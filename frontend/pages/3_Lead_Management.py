"""
Cynbit AI - Lead Management Page
Search, filter, update CRM status, and export leads to CSV via REST API.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
from frontend.utils.api_client import api_client, APIClientError
from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar
from frontend.components.cards import render_priority_badge

st.set_page_config(page_title="Lead Management | Cynbit AI", page_icon="🗂️", layout="wide")
apply_cynbit_theme()
render_sidebar()

st.title("🗂️ Lead Pipeline Management")
st.markdown("Search, filter, update qualification stages, and export persistent lead records via the REST API.")

def format_date_str(val, fmt="%Y-%m-%d %H:%M:%S"):
    """Safely formats ISO string or datetime object."""
    if not val:
        return ""
    if isinstance(val, str):
        try:
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            return dt.strftime(fmt)
        except Exception:
            return val[:19]
    if hasattr(val, "strftime"):
        return val.strftime(fmt)
    return str(val)

# 1. Filter Toolbar
col_f1, col_f2, col_f3, col_f4 = st.columns([1.5, 1, 1, 1])

with col_f1:
    search_term = st.text_input("🔍 Search Leads", placeholder="Client name, company, or keyword...")

with col_f2:
    category_filter = st.selectbox(
        "Service Category",
        ["All", "AI/ML Development", "Web Development", "Mobile App Development", "Cloud & DevOps", "Business Automation", "Other"]
    )

with col_f3:
    priority_filter = st.selectbox(
        "Priority Tier",
        ["All", "Hot", "Warm", "Cold"]
    )

with col_f4:
    status_filter = st.selectbox(
        "CRM Status",
        ["All", "New", "Contacted", "Qualified", "Proposal Sent", "Negotiation", "Closed-Won", "Closed-Lost"]
    )

# Fetch leads via API
try:
    leads = api_client.list_leads(
        search=search_term if search_term.strip() else None,
        category=category_filter,
        priority=priority_filter,
        status=status_filter,
        limit=200
    )
except APIClientError as e:
    st.error(f"⚠️ Error fetching leads from backend: {e}")
    leads = []

# Export to CSV Toolbar
col_count, col_export = st.columns([3, 1])
with col_count:
    st.markdown(f"**Found {len(leads)} matching leads**")
with col_export:
    if leads:
        df_export = pd.DataFrame([
            {
                "Lead ID": l.get("lead_id", ""),
                "Date Created": format_date_str(l.get("created_at")),
                "Client Name": l.get("client_name", ""),
                "Email": l.get("client_email", ""),
                "Company": l.get("client_company", ""),
                "Category": l.get("service_category", ""),
                "Score": l.get("score", 0),
                "Priority": l.get("priority", ""),
                "Status": l.get("status", ""),
                "Budget": l.get("budget_raw", ""),
                "Timeline": l.get("timeline_raw", ""),
                "Urgency": l.get("urgency_level", ""),
                "Intent": l.get("customer_intent", ""),
                "Inquiry": l.get("inquiry_text", ""),
                "Notes": l.get("notes", "")
            }
            for l in leads
        ])
        csv_bytes = df_export.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Export to CSV",
            data=csv_bytes,
            file_name="cynbit_qualified_leads.csv",
            mime="text/csv",
            use_container_width=True
        )

# Data Table Display
if leads:
    table_rows = []
    for l in leads:
        table_rows.append({
            "Lead ID": l.get("lead_id", ""),
            "Client Name": l.get("client_name", ""),
            "Company": l.get("client_company", ""),
            "Category": l.get("service_category", ""),
            "Score": l.get("score", 0),
            "Priority": l.get("priority", ""),
            "Budget": l.get("budget_raw", "Unspecified"),
            "Urgency": l.get("urgency_level", "Medium"),
            "Status": l.get("status", "New"),
            "Created": format_date_str(l.get("created_at"), "%Y-%m-%d")
        })
    df_display = pd.DataFrame(table_rows)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Inline Quick Lead Status Updater via API
    st.subheader("⚡ Quick Lead Action")
    col_u1, col_u2, col_u3, col_u4 = st.columns([1.5, 1.2, 1.2, 0.8])
    
    lead_options = [f"{l['lead_id']} - {l.get('client_name', 'Lead')} ({l.get('service_category', 'Other')})" for l in leads]
    with col_u1:
        selected_lead_str = st.selectbox("Select Lead to Update:", lead_options)
        selected_lead_id = selected_lead_str.split(" - ")[0] if selected_lead_str else ""
        
    with col_u2:
        new_status = st.selectbox(
            "Change CRM Status:",
            ["New", "Contacted", "Qualified", "Proposal Sent", "Negotiation", "Closed-Won", "Closed-Lost"]
        )
        
    with col_u3:
        update_notes = st.text_input("Append Log Note:", placeholder="e.g. Discovery call completed")
        
    with col_u4:
        st.markdown("<div style='height: 28px;'></div>", unsafe_allow_html=True)
        if st.button("Update Lead", use_container_width=True):
            try:
                # Find current notes
                lead_matches = [l for l in leads if l["lead_id"] == selected_lead_id]
                existing_notes = lead_matches[0].get("notes", "") if lead_matches else ""
                combined_notes = f"{existing_notes} | {update_notes}".strip(" |") if update_notes else existing_notes
                
                with st.spinner("Updating lead status via API..."):
                    api_client.update_lead(
                        lead_identifier=selected_lead_id,
                        status=new_status,
                        notes=combined_notes
                    )
                st.success(f"Updated {selected_lead_id} status to '{new_status}'!")
                st.rerun()
            except APIClientError as e:
                st.error(f"Error updating lead: {e}")
else:
    st.info("No leads match the selected criteria.")
