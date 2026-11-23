"""
Cynbit AI - Lead Management Page
Search, filter, update CRM status, and export leads to CSV.
"""

import streamlit as st
import pandas as pd
from app.database import SessionLocal
from app.routes.leads import list_leads, update_lead, delete_lead
from app.schemas.lead import LeadUpdateRequest
from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar
from frontend.components.cards import render_priority_badge

st.set_page_config(page_title="Lead Management | Cynbit AI", page_icon="🗂️", layout="wide")
apply_cynbit_theme()
render_sidebar()

st.title("🗂️ Lead Pipeline Management")
st.markdown("Search, filter, update qualification stages, and export persistent lead records.")

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

db = SessionLocal()
try:
    leads = list_leads(
        search=search_term if search_term.strip() else None,
        category=category_filter,
        priority=priority_filter,
        status=status_filter,
        limit=200,
        db=db
    )
finally:
    db.close()

# Export to CSV Toolbar
col_count, col_export = st.columns([3, 1])
with col_count:
    st.markdown(f"**Found {len(leads)} matching leads**")
with col_export:
    if leads:
        # Convert leads to DataFrame for instant CSV export
        df_export = pd.DataFrame([
            {
                "Lead ID": l["lead_id"],
                "Date Created": l["created_at"].strftime("%Y-%m-%d %H:%M:%S") if l.get("created_at") else "",
                "Client Name": l["client_name"],
                "Email": l["client_email"],
                "Company": l["client_company"],
                "Category": l["service_category"],
                "Score": l["score"],
                "Priority": l["priority"],
                "Status": l["status"],
                "Budget": l["budget_raw"],
                "Timeline": l["timeline_raw"],
                "Urgency": l["urgency_level"],
                "Intent": l["customer_intent"],
                "Inquiry": l["inquiry_text"],
                "Notes": l["notes"]
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
            "Lead ID": l["lead_id"],
            "Client Name": l["client_name"],
            "Company": l["client_company"],
            "Category": l["service_category"],
            "Score": l["score"],
            "Priority": l["priority"],
            "Budget": l["budget_raw"],
            "Urgency": l["urgency_level"],
            "Status": l["status"],
            "Created": l["created_at"].strftime("%Y-%m-%d") if l.get("created_at") else ""
        })
    df_display = pd.DataFrame(table_rows)
    st.dataframe(df_display, use_container_width=True, hide_index=True)
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    
    # Inline Quick Lead Status Updater
    st.subheader("⚡ Quick Lead Action")
    col_u1, col_u2, col_u3, col_u4 = st.columns([1.5, 1.2, 1.2, 0.8])
    
    lead_options = [f"{l['lead_id']} - {l['client_name']} ({l['service_category']})" for l in leads]
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
            db = SessionLocal()
            try:
                # Find current notes
                lead_obj = [l for l in leads if l["lead_id"] == selected_lead_id][0]
                existing_notes = lead_obj.get("notes", "")
                combined_notes = f"{existing_notes} | {update_notes}".strip(" |") if update_notes else existing_notes
                
                req = LeadUpdateRequest(status=new_status, notes=combined_notes)
                update_lead(selected_lead_id, req, db=db)
                st.success(f"Updated {selected_lead_id} status to '{new_status}'!")
                st.rerun()
            except Exception as e:
                st.error(f"Error updating lead: {e}")
            finally:
                db.close()
else:
    st.info("No leads match the selected criteria.")
