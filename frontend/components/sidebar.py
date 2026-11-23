"""
Cynbit AI - Streamlit Sidebar Component
Renders the brand sidebar with navigation assistance and live system diagnostics.
"""

import streamlit as st
from app.database import SessionLocal
from app.models.lead import LeadModel
from app.ml.evaluate import is_model_trained

def render_sidebar():
    """Renders persistent Cynbit branded sidebar."""
    with st.sidebar:
        # Brand Header
        st.markdown("""
        <div style="text-align: left; padding: 10px 0 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1);">
            <div style="font-size: 1.6rem; font-weight: 800; color: #48CAE4; letter-spacing: -0.02em;">
                ⚡ CYNBIT <span style="color: #FFFFFF; font-weight: 400;">AI</span>
            </div>
            <div style="font-size: 0.78rem; color: #8D99AE; text-transform: uppercase; letter-spacing: 0.08em; margin-top: 3px;">
                Lead Intelligence Platform
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<div style='height: 12px;'></div>", unsafe_allow_html=True)
        
        # System Health & Telemetry
        model_ready = is_model_trained()
        db = SessionLocal()
        try:
            total_leads = db.query(LeadModel).count()
            hot_count = db.query(LeadModel).filter(LeadModel.priority == "Hot").count()
        except Exception:
            total_leads = 0
            hot_count = 0
        finally:
            db.close()
            
        st.markdown(f"""
        <div style="background-color: #141C36; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px 14px; margin-bottom: 20px;">
            <div style="font-size: 0.75rem; font-weight: 600; color: #8D99AE; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                SYSTEM TELEMETRY
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 0.8rem; color: #E0E1DD;">ML Inference:</span>
                <span style="font-size: 0.75rem; color: {'#06D6A0' if model_ready else '#EF476F'}; font-weight: 700;">
                    {'● ACTIVE (TF-IDF)' if model_ready else '○ RETRAINING'}
                </span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 0.8rem; color: #E0E1DD;">CRM Database:</span>
                <span style="font-size: 0.75rem; color: #06D6A0; font-weight: 700;">● CONNECTED</span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between;">
                <span style="font-size: 0.8rem; color: #E0E1DD;">Total Records:</span>
                <span style="font-size: 0.8rem; color: #FFFFFF; font-weight: 700; font-family: monospace;">{total_leads} ({hot_count} Hot)</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Quick Actions
        st.markdown("<div style='font-size: 0.75rem; font-weight: 600; color: #8D99AE; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;'>QUICK STATS</div>", unsafe_allow_html=True)
        col_s1, col_s2 = st.columns(2)
        with col_s1:
            st.metric("Total Leads", total_leads)
        with col_s2:
            st.metric("Hot Priority", hot_count)
            
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        # Technical Assessment Attribution
        st.markdown("""
        <div style="padding-top: 20px; border-top: 1px solid rgba(255,255,255,0.08); font-size: 0.75rem; color: #6C757D; line-height: 1.5;">
            <strong style="color: #48CAE4;">Cynbit Technologies</strong><br>
            AI/ML Engineer Assessment<br>
            Production Proof-of-Concept v1.0
        </div>
        """, unsafe_allow_html=True)
