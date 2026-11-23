"""
Cynbit AI - Add New Lead & Live AI Intelligence Form
Submits customer inquiries to the backend API for real-time ML analysis and CRM persistence.
"""

import streamlit as st
import json
from frontend.utils.api_client import api_client, APIClientError
from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar
from frontend.components.cards import render_priority_badge, render_score_badge
from frontend.components.charts import create_score_breakdown_bar

st.set_page_config(page_title="Add New Lead | Cynbit AI", page_icon="✨", layout="wide")
apply_cynbit_theme()
render_sidebar()

st.title("✨ AI Lead Analyzer & Intake")
st.markdown("Analyze incoming customer inquiries in real time with Cynbit's NLP Classification, Entity Extraction, and Multi-Factor Scoring Engine.")

# Quick Demo Preset Templates
PRESETS = {
    "Select a pre-loaded business inquiry...": "",
    "AI/ML Defect Detection": "We are looking for an AI team to build a custom computer vision model for defect detection on our manufacturing assembly line. We process 500 parts per minute and need inference speed under 50ms. Budget is around $45,000 and we need an initial prototype within 8 weeks.",
    "AWS Multi-Service Cloud Migration": "We need to migrate our on-premise infrastructure to AWS. We currently have 40 virtual machines, a monolithic MySQL database, and legacy filesystems. Looking for Terraform infrastructure-as-code, Dockerization, and zero-downtime database migration. Budget $35,000, timeline 2 months.",
    "B2B Intelligent Document Automation": "We spend 40 hours a week manually copying invoice data from incoming supplier PDFs into QuickBooks and SAP. We need an automated intelligent document processing (IDP) workflow that extracts line items, validates totals, and automatically pushes to SAP. Budget $25,000, timeline 6 weeks.",
    "Cross-Platform Telemedicine Mobile App": "We want to build a cross-platform mobile app in Flutter for both iOS and Android. It is a telemedicine app with video calling, prescription history, and push notifications. Budget $35,000, timeline 3 months.",
    "Next.js High-Conversion Web Portal": "We need a full-stack web application for our real estate agency. Features should include interactive map search, virtual tours, mortgage calculator, and CRM integration. We prefer Next.js and Tailwind CSS. Budget $25,000, timeline 2 months."
}

col_preset, _ = st.columns([2, 1])
with col_preset:
    selected_preset = st.selectbox("🎯 Quick Demo Templates (Click to auto-fill):", list(PRESETS.keys()))

default_inquiry = PRESETS[selected_preset] if selected_preset != "Select a pre-loaded business inquiry..." else ""

# Input Form
with st.form("lead_analysis_form"):
    col1, col2, col3 = st.columns(3)
    with col1:
        client_name = st.text_input("Contact Full Name", value="Alexander Wright" if default_inquiry else "", placeholder="e.g. Sarah Jenkins")
    with col2:
        client_email = st.text_input("Contact Email", value="a.wright@enterprise.com" if default_inquiry else "", placeholder="e.g. s.jenkins@company.com")
    with col3:
        client_company = st.text_input("Company / Organization", value="Vanguard Dynamics Corp" if default_inquiry else "", placeholder="e.g. Aura Health Inc.")

    inquiry_text = st.text_area(
        "Customer Inquiry Text *",
        value=default_inquiry,
        height=140,
        placeholder="Paste customer project inquiry, RFQ, email, or contact form message here..."
    )
    
    col_opt1, col_opt2 = st.columns(2)
    with col_opt1:
        manual_cat = st.selectbox(
            "Service Category Override (Optional)",
            ["Auto-Detect with AI", "AI/ML Development", "Web Development", "Mobile App Development", "Cloud & DevOps", "Business Automation", "Other"]
        )
    with col_opt2:
        notes = st.text_input("Internal Sales Notes (Optional)", placeholder="e.g. Referred by Partner Network")
        
    submitted = st.form_submit_button("⚡ Analyze Inquiry with AI", use_container_width=True)

# Analysis Execution & Display
if submitted or (inquiry_text and default_inquiry and "last_analyzed" not in st.session_state):
    if not inquiry_text.strip():
        st.error("Please enter inquiry text to analyze.")
    else:
        chosen_cat = None if manual_cat == "Auto-Detect with AI" else manual_cat
        try:
            with st.spinner("Analyzing inquiry with Cynbit ML Engine..."):
                result = api_client.analyze_inquiry(
                    inquiry_text=inquiry_text,
                    client_name=client_name,
                    client_email=client_email,
                    client_company=client_company,
                    manual_category=chosen_cat
                )
                st.session_state["current_analysis"] = result
                st.session_state["last_analyzed"] = True
        except APIClientError as e:
            st.error(f"Analysis failed: {e}")

if "current_analysis" in st.session_state:
    res = st.session_state["current_analysis"]
    
    st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
    st.markdown("### 📋 AI Lead Intelligence Results")
    
    # Score & Key Metrics Banner
    st.markdown(f"""
    <div style="background: linear-gradient(135deg, #16203D 0%, #0F172E 100%); border: 1px solid rgba(72,202,228,0.3); border-radius: 12px; padding: 22px 28px; margin-bottom: 22px;">
        <div style="display: flex; justify-content: space-between; align-items: center; flex-wrap: wrap; gap: 15px;">
            <div>
                <div style="font-size: 0.85rem; color: #8D99AE; text-transform: uppercase; font-weight: 700; letter-spacing: 0.05em;">
                    LEAD QUALIFICATION SCORE
                </div>
                <div style="font-size: 2.8rem; font-weight: 800; color: #FFFFFF; font-family: 'JetBrains Mono', monospace;">
                    {res.get('score', 0)} <span style="font-size: 1.2rem; color: #8D99AE;">/ 100</span>
                </div>
            </div>
            <div>
                <div style="font-size: 0.85rem; color: #8D99AE; text-transform: uppercase; font-weight: 700; margin-bottom: 6px;">
                    PRIORITY TIER
                </div>
                <div>{render_priority_badge(res.get('priority', 'Warm'))}</div>
            </div>
            <div>
                <div style="font-size: 0.85rem; color: #8D99AE; text-transform: uppercase; font-weight: 700;">
                    SERVICE CLASSIFICATION
                </div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #48CAE4;">
                    {res.get('service_category', 'Other')} <span style="font-size: 0.85rem; color: #06D6A0;">({res.get('category_confidence', 0.0)*100:.1f}% confidence)</span>
                </div>
            </div>
            <div>
                <div style="font-size: 0.85rem; color: #8D99AE; text-transform: uppercase; font-weight: 700;">
                    ESTIMATED BUDGET
                </div>
                <div style="font-size: 1.25rem; font-weight: 700; color: #FFFFFF; font-family: monospace;">
                    {res.get('budget_raw', 'Unspecified')}
                </div>
            </div>
        </div>
        <div style="margin-top: 15px; padding-top: 12px; border-top: 1px solid rgba(255,255,255,0.08); font-size: 0.9rem; color: #CCD6F6;">
            <strong>Action Recommendation:</strong> {res.get('action_recommendation', 'Follow up promptly.')}
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Details Columns
    col_d1, col_d2 = st.columns([1.1, 1.2])
    
    with col_d1:
        st.subheader("Extracted Entity Breakdown")
        st.markdown(f"**Customer Intent:** `{res.get('customer_intent', 'Commercial Project')}`")
        st.markdown(f"**Target Timeline:** `{res.get('timeline_raw', 'Flexible')}`")
        st.markdown(f"**Urgency Level:** `{res.get('urgency_level', 'Medium')}`")
        
        techs = res.get("detected_technologies", [])
        if techs:
            st.markdown(f"**Detected Technologies:** {', '.join([f'`{t}`' for t in techs])}")
            
        reqs = res.get("extracted_requirements", [])
        if reqs:
            st.markdown("**Key Requirements Identified:**")
            for r in reqs:
                st.markdown(f"- {r}")
                
        st.markdown("**Score Justification:**")
        for r in res.get("score_reasons", []):
            st.markdown(f"- {r}")
            
    with col_d2:
        st.subheader("Score Factor Contributions")
        breakdown = res.get("score_breakdown", {})
        if breakdown:
            fig_score = create_score_breakdown_bar(breakdown)
            st.plotly_chart(fig_score, use_container_width=True)
        
    # Suggested Response Preview & Save to DB
    st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
    st.subheader("✉️ AI-Generated Proposal / Response")
    st.caption(f"Generated via: {res.get('response_engine', 'Cynbit Engine')}")
    
    resp_text = st.text_area("Client Response Preview (Editable)", value=res.get("suggested_response", ""), height=220)
    
    # Save to CRM Database Button via API
    if st.button("💾 Save Lead to CRM Database", use_container_width=True):
        try:
            with st.spinner("Saving lead to backend CRM..."):
                saved = api_client.create_lead(
                    inquiry_text=res.get("inquiry_text", inquiry_text),
                    client_name=res.get("client_name") or "Inbound Lead",
                    client_email=res.get("client_email", ""),
                    client_company=res.get("client_company", ""),
                    manual_category=res.get("service_category"),
                    notes=notes
                )
                st.success(f"✅ Lead successfully saved! Assigned ID: **{saved.get('lead_id')}**")
        except APIClientError as e:
            st.error(f"Failed to save lead: {e}")
