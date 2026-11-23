"""
Cynbit AI - Lead Intelligence Deep Dive Page
Provides granular 360-degree inspection for any individual qualified lead via REST API.
"""

import streamlit as st
import json
from datetime import datetime
from frontend.utils.api_client import api_client, APIClientError
from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar
from frontend.components.cards import render_priority_badge, render_score_badge
from frontend.components.charts import create_score_breakdown_bar

st.set_page_config(page_title="Lead Intelligence | Cynbit AI", page_icon="🔍", layout="wide")
apply_cynbit_theme()
render_sidebar()

st.title("🔍 Lead Intelligence & Scoring Deep-Dive")
st.markdown("Inspect granular entity extractions, mathematical score weights, and tailored proposal drafts.")

def format_date_str(val, fmt="%Y-%m-%d %H:%M"):
    """Safely formats ISO string or datetime object."""
    if not val:
        return ""
    if isinstance(val, str):
        try:
            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
            return dt.strftime(fmt)
        except Exception:
            return val[:16]
    if hasattr(val, "strftime"):
        return val.strftime(fmt)
    return str(val)

# Fetch leads via API
try:
    all_leads = api_client.list_leads(limit=100, sort_by="score", order="desc")
except APIClientError as e:
    st.error(f"⚠️ Could not load leads from backend: {e}")
    all_leads = []

if not all_leads:
    st.warning("No leads found in database. Please add or seed leads first.")
    if st.button("🌱 Seed Sample Leads Now"):
        try:
            api_client.seed_leads(force=True)
            st.success("Sample leads seeded successfully! Refreshing...")
            st.rerun()
        except APIClientError as e:
            st.error(f"Failed to seed leads: {e}")
    st.stop()

# Selector for lead
lead_options = {
    f"{l['lead_id']} | {l.get('client_name', 'Lead')} ({l.get('client_company', 'N/A')}) - {l.get('service_category', 'Other')} [Score: {l.get('score', 0)}]": l["lead_id"]
    for l in all_leads
}
selected_label = st.selectbox("Select a Lead to Inspect:", list(lead_options.keys()))
lead_id = lead_options[selected_label]

# Fetch full details via API
try:
    lead = api_client.get_lead(lead_id)
except APIClientError as e:
    st.error(f"Could not load details for lead {lead_id}: {e}")
    st.stop()

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Top Summary Header
col_h1, col_h2, col_h3, col_h4 = st.columns([1.5, 1, 1, 1])

with col_h1:
    st.markdown(f"### {lead.get('client_name', 'Lead')}")
    st.markdown(f"**Company:** {lead.get('client_company') or 'N/A'} | **Email:** `{lead.get('client_email') or 'N/A'}`")
    st.caption(f"Lead ID: `{lead.get('lead_id')}` | Created: {format_date_str(lead.get('created_at'))}")

with col_h2:
    st.markdown("**Priority & Score**")
    st.markdown(render_priority_badge(lead.get("priority", "Warm")), unsafe_allow_html=True)
    st.markdown(render_score_badge(lead.get("score", 0)), unsafe_allow_html=True)

with col_h3:
    st.markdown("**Service Category**")
    st.markdown(f"#### {lead.get('service_category', 'Other')}")
    st.caption(f"ML Confidence: {lead.get('category_confidence', 0.0)*100:.1f}%")

with col_h4:
    st.markdown("**Commercial Parameters**")
    st.markdown(f"**Budget:** `{lead.get('budget_raw', 'Unspecified')}`")
    st.markdown(f"**Timeline:** `{lead.get('timeline_raw', 'Flexible')}`")
    st.markdown(f"**Urgency:** `{lead.get('urgency_level', 'Medium')}`")

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# 2 Columns: Left = Inquiry & Entities, Right = Scoring Analysis
col_left, col_right = st.columns([1.1, 1.2])

with col_left:
    st.subheader("📝 Original Client Inquiry")
    st.markdown(f"""
    <div style="background-color: #141C36; border-left: 3px solid #48CAE4; border-radius: 6px; padding: 16px 20px; font-size: 0.95rem; line-height: 1.6; color: #E0E1DD;">
        "{lead.get('inquiry_text', '')}"
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.subheader("🧩 Extracted Business Entities")
    
    st.markdown(f"**Customer Intent:** `{lead.get('customer_intent', 'N/A')}`")
    
    techs = lead.get("detected_technologies", [])
    if techs:
        st.markdown(f"**Target Technologies:** {', '.join([f'`{t}`' for t in techs])}")
        
    reqs = lead.get("extracted_requirements", [])
    if reqs:
        st.markdown("**Identified Scope & Constraints:**")
        for r in reqs:
            st.markdown(f"- {r}")

with col_right:
    st.subheader("📊 Lead Scoring Matrix")
    
    breakdown = lead.get("score_breakdown", {})
    if breakdown:
        fig_breakdown = create_score_breakdown_bar(breakdown)
        st.plotly_chart(fig_breakdown, use_container_width=True)
        
    st.markdown("**Qualification Rationales:**")
    for reason in lead.get("score_reasons", []):
        st.markdown(f"- {reason}")
        
    st.info(f"💡 **Action Recommendation:** {lead.get('action_recommendation', 'Engage via standard discovery call.')}")

st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)

# AI Response Preview & Action
st.subheader("✉️ Tailored AI Business Response")
st.caption(f"Engine: {lead.get('response_engine', 'Cynbit Rule Engine')}")

edited_response = st.text_area("Client Proposal / Reply Draft", value=lead.get("suggested_response", ""), height=240)

col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
with col_act1:
    if st.button("💾 Save Response Draft", use_container_width=True):
        try:
            with st.spinner("Saving response draft via API..."):
                existing_notes = lead.get("notes", "")
                timestamp_str = datetime.utcnow().strftime("%Y-%m-%d %H:%M")
                note_update = f"{existing_notes} | Draft updated at {timestamp_str}".strip(" |")
                api_client.update_lead(
                    lead_identifier=lead["lead_id"],
                    notes=note_update
                )
                st.success("Draft response saved to CRM record!")
        except APIClientError as e:
            st.error(f"Save failed: {e}")

with col_act2:
    if st.button("🚀 Simulate Send to Client", use_container_width=True):
        st.toast(f"Proposal sent to {lead.get('client_email') or lead.get('client_name')}!", icon="✅")
        st.success(f"Response successfully dispatched to {lead.get('client_name')}.")
