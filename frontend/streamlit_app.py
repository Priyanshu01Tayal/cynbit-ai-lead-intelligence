
"""
Cynbit AI - Main Streamlit Entrypoint
Directs users to the Executive Dashboard with brand overview.
"""

import sys
from pathlib import Path

import streamlit as st


# ============================================================
# PROJECT ROOT CONFIGURATION
# Fix ModuleNotFoundError on Streamlit Community Cloud
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


# ============================================================
# PROJECT IMPORTS
# ============================================================

from frontend.components.styles import apply_cynbit_theme
from frontend.components.sidebar import render_sidebar


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Cynbit AI | Lead Intelligence & Automation",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# APPLY THEME AND SIDEBAR
# ============================================================

apply_cynbit_theme()
render_sidebar()


# ============================================================
# HERO SECTION
# ============================================================

st.markdown(
    """
    <div style="
        background: linear-gradient(135deg, #162244 0%, #0F172E 100%);
        border: 1px solid rgba(72, 202, 228, 0.3);
        border-radius: 14px;
        padding: 32px 36px;
        margin-bottom: 28px;
    ">

        <div style="
            font-size: 0.85rem;
            font-weight: 700;
            color: #48CAE4;
            text-transform: uppercase;
            letter-spacing: 0.1em;
            margin-bottom: 8px;
        ">
            CYNBIT TECHNOLOGIES • AI & AUTOMATION PLATFORM
        </div>

        <div style="
            font-size: 2.4rem;
            font-weight: 800;
            color: #FFFFFF;
            line-height: 1.2;
            margin-bottom: 14px;
        ">
            Intelligent Lead Qualification & Automation Agent
        </div>

        <div style="
            font-size: 1.05rem;
            color: #CCD6F6;
            max-width: 880px;
            line-height: 1.6;
        ">
            Welcome to Cynbit's next-generation client intelligence system.
            Using Scikit-Learn NLP text classification, heuristic entity
            extraction, and multidimensional lead scoring, this platform
            automates the qualification of incoming business inquiries,
            estimates budgets, prioritizes sales pipelines, and drafts
            executive-grade proposals in seconds.
        </div>

    </div>
    """,
    unsafe_allow_html=True
)


# ============================================================
# PLATFORM CAPABILITIES
# ============================================================

st.subheader("Platform Capabilities")

col1, col2, col3 = st.columns(3)


# Executive Dashboard Card
with col1:
    st.markdown(
        """
        <div class="cynbit-card">

            <h4 style="color: #48CAE4; margin-top: 0;">
                📊 Executive Dashboard
            </h4>

            <p style="color: #CCD6F6; font-size: 0.9rem;">
                High-level KPI metrics, real-time lead priority breakdown
                (Hot / Warm / Cold), service demand distributions, and
                conversion funnel analytics.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# AI Lead Analyzer Card
with col2:
    st.markdown(
        """
        <div class="cynbit-card">

            <h4 style="color: #48CAE4; margin-top: 0;">
                ✨ AI Lead Analyzer
            </h4>

            <p style="color: #CCD6F6; font-size: 0.9rem;">
                Test incoming inquiry text in real-time. Instantly extract
                technical stack requirements, budget estimates, urgency,
                and generate personalized proposal drafts.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# Model Performance Card
with col3:
    st.markdown(
        """
        <div class="cynbit-card">

            <h4 style="color: #48CAE4; margin-top: 0;">
                🤖 Model Performance
            </h4>

            <p style="color: #CCD6F6; font-size: 0.9rem;">
                Inspect genuine held-out test evaluation metrics
                (Accuracy, Precision, Recall, F1), view the Confusion
                Matrix, and trigger on-demand model retraining.
            </p>

        </div>
        """,
        unsafe_allow_html=True
    )


# ============================================================
# FOOTER / NAVIGATION MESSAGE
# ============================================================

st.markdown(
    "<div style='height: 15px;'></div>",
    unsafe_allow_html=True
)

st.info(
    "👈 Use the sidebar navigation to explore the different pages of the application."
)
