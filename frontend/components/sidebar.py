"""
Cynbit AI - Streamlit Sidebar Component
Renders the brand sidebar with navigation assistance and live system diagnostics via REST API.
"""

import streamlit as st
from frontend.utils.api_client import api_client, APIClientError

def render_sidebar():
    """Renders persistent Cynbit branded sidebar connected to FastAPI backend."""
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
        
        # System Health & Telemetry via API
        backend_connected = False
        model_ready = False
        total_leads = 0
        hot_count = 0
        
        try:
            health = api_client.get_health()
            backend_connected = (health.get("status") == "healthy")
            model_ready = health.get("model_loaded", False)
            total_leads = health.get("lead_count", 0)
            
            # Fetch hot count from analytics summary
            summary = api_client.get_analytics_summary()
            hot_count = summary.get("hot_leads", 0)
            total_leads = summary.get("total_leads", total_leads)
        except Exception:
            # Backend may be starting or offline
            backend_connected = False
            model_ready = False
            total_leads = 0
            hot_count = 0

        # Display host indicator
        host_display = api_client.base_url.replace("https://", "").replace("http://", "")
        if len(host_display) > 28:
            host_display = host_display[:25] + "..."
            
        st.markdown(f"""
        <div style="background-color: #141C36; border: 1px solid rgba(255,255,255,0.08); border-radius: 8px; padding: 12px 14px; margin-bottom: 20px;">
            <div style="font-size: 0.75rem; font-weight: 600; color: #8D99AE; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 8px;">
                SYSTEM TELEMETRY
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 0.8rem; color: #E0E1DD;">ML Inference:</span>
                <span style="font-size: 0.75rem; color: {'#06D6A0' if model_ready else '#EF476F'}; font-weight: 700;">
                    {'● ACTIVE (TF-IDF)' if model_ready else '○ OFFLINE'}
                </span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 0.8rem; color: #E0E1DD;">Backend API:</span>
                <span style="font-size: 0.75rem; color: {'#06D6A0' if backend_connected else '#EF476F'}; font-weight: 700;">
                    {'● CONNECTED' if backend_connected else '○ CONNECTING...'}
                </span>
            </div>
            <div style="display: flex; align-items: center; justify-content: space-between; margin-bottom: 6px;">
                <span style="font-size: 0.8rem; color: #E0E1DD;">Host:</span>
                <span style="font-size: 0.72rem; color: #48CAE4; font-family: monospace; font-weight: 600;" title="{api_client.base_url}">
                    {host_display}
                </span>
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
