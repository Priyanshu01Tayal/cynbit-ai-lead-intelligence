"""
Cynbit AI - Lead Intelligence Deep Dive Page
Provides granular 360-degree inspection for any individual qualified lead.
"""

import streamlit as st
import json
from app.database import SessionLocal
from app.routes.leads import list_leads, get_lead, update_lead
from app.schemas.lead import LeadUpdateRequest
from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar
from frontend.components.cards import render_priority_badge, render_score_badge
from frontend.components.charts import create_score_breakdown_bar

st.set_page_config(page_title="Lead Intelligence | Cynbit AI", page_icon="🔍", layout="wide")
apply_cynbit_theme()
render_sidebar()

st.title("🔍 Lead Intelligence & Scoring Deep-Dive")
st.markdown("Inspect granular entity extractions, mathematical score weights, and tailored proposal drafts.")

db = SessionLocal()
try:
    all_leads = list_leads(limit=100, sort_by="score", order="desc", db=db)
finally:
    db.close()

if not all_leads:
    st.warning("No leads found in database. Please add or seed leads first.")
    st.stop()

# Selector for lead
lead_options = {f"{l['lead_id']} | {l['client_name']} ({l['client_company']}) - {l['service_category']} [Score: {l['score']}]": l["lead_id"] for l in all_leads}
selected_label = st.selectbox("Select a Lead to Inspect:", list(lead_options.keys()))
lead_id = lead_options[selected_label]

# Fetch full details
db = SessionLocal()
try:
    lead = get_lead(lead_id, db=db)
finally:
    db.close()

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# Top Summary Header
col_h1, col_h2, col_h3, col_h4 = st.columns([1.5, 1, 1, 1])

with col_h1:
    st.markdown(f"### {lead['client_name']}")
    st.markdown(f"**Company:** {lead['client_company'] or 'N/A'} | **Email:** `{lead['client_email'] or 'N/A'}`")
    st.caption(f"Lead ID: `{lead['lead_id']}` | Created: {lead['created_at'].strftime('%Y-%m-%d %H:%M')}")

with col_h2:
    st.markdown("**Priority & Score**")
    st.markdown(render_priority_badge(lead["priority"]), unsafe_allow_html=True)
    st.markdown(render_score_badge(lead["score"]), unsafe_allow_html=True)

with col_h3:
    st.markdown("**Service Category**")
    st.markdown(f"#### {lead['service_category']}")
    st.caption(f"ML Confidence: {lead['category_confidence']*100:.1f}%")

with col_h4:
    st.markdown("**Commercial Parameters**")
    st.markdown(f"**Budget:** `{lead['budget_raw']}`")
    st.markdown(f"**Timeline:** `{lead['timeline_raw']}`")
    st.markdown(f"**Urgency:** `{lead['urgency_level']}`")

st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)

# 2 Columns: Left = Inquiry & Entities, Right = Scoring Analysis
col_left, col_right = st.columns([1.1, 1.2])

with col_left:
    st.subheader("📝 Original Client Inquiry")
    st.markdown(f"""
    <div style="background-color: #141C36; border-left: 3px solid #48CAE4; border-radius: 6px; padding: 16px 20px; font-size: 0.95rem; line-height: 1.6; color: #E0E1DD;">
        "{lead['inquiry_text']}"
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.subheader("🧩 Extracted Business Entities")
    
    st.markdown(f"**Customer Intent:** `{lead['customer_intent']}`")
    
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

edited_response = st.text_area("Client Proposal / Reply Draft", value=lead["suggested_response"], height=240)

col_act1, col_act2, col_act3 = st.columns([1, 1, 2])
with col_act1:
    if st.button("💾 Save Response Draft", use_container_width=True):
        db = SessionLocal()
        try:
            req = LeadUpdateRequest(notes=f"Draft response updated at {st.session_state.get('time', 'recent')}")
            # Update response directly in model
            from app.models.lead import LeadModel
            lead_db = db.query(LeadModel).filter(LeadModel.lead_id == lead["lead_id"]).first()
            if lead_db:
                lead_db.suggested_response = edited_response
                db.commit()
                st.success("Draft response saved!")
        except Exception as e:
            st.error(f"Save failed: {e}")
        finally:
            db.close()

with col_act2:
    if st.button("🚀 Simulate Send to Client", use_container_width=True):
        st.toast(f"Proposal sent to {lead['client_email'] or lead['client_name']}!", icon="✅")
        st.success(f"Response successfully dispatched to {lead['client_name']}.")
