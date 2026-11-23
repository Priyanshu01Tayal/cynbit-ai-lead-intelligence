"""
Cynbit AI - Streamlit Styling & Theme Utilities
Defines the modern Dark Navy & Cyan/Blue Accent design system.
"""

import streamlit as st

CYNBIT_CSS = """
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Main Container Background */
    .stApp {
        background-color: #0B132B;
        color: #F8F9FA;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #0E1838 !important;
        border-right: 1px solid rgba(255, 255, 255, 0.08);
    }

    section[data-testid="stSidebar"] div[data-testid="stMarkdownContainer"] {
        color: #E0E1DD;
    }

    /* Card Containers */
    .cynbit-card {
        background: linear-gradient(135deg, rgba(28, 37, 65, 0.7) 0%, rgba(20, 27, 48, 0.9) 100%);
        border: 1px solid rgba(72, 202, 228, 0.18);
        border-radius: 12px;
        padding: 22px 24px;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.28);
        margin-bottom: 20px;
        backdrop-filter: blur(10px);
    }

    .cynbit-kpi-card {
        background: linear-gradient(145deg, #16203D 0%, #0F172E 100%);
        border: 1px solid rgba(58, 134, 255, 0.25);
        border-radius: 12px;
        padding: 20px 22px;
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .cynbit-kpi-card:hover {
        border-color: #48CAE4;
        transform: translateY(-2px);
    }

    .kpi-title {
        font-size: 0.85rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        color: #8D99AE;
        margin-bottom: 6px;
    }

    .kpi-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #FFFFFF;
        line-height: 1.1;
        font-family: 'JetBrains Mono', monospace;
    }

    .kpi-subtext {
        font-size: 0.82rem;
        color: #48CAE4;
        margin-top: 6px;
        font-weight: 500;
    }

    /* Priority Badges */
    .badge-hot {
        background: linear-gradient(135deg, rgba(239, 71, 111, 0.25) 0%, rgba(239, 71, 111, 0.45) 100%);
        border: 1px solid #EF476F;
        color: #FFB3C1;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }

    .badge-warm {
        background: linear-gradient(135deg, rgba(255, 183, 3, 0.2) 0%, rgba(255, 183, 3, 0.4) 100%);
        border: 1px solid #FFB703;
        color: #FFE699;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 700;
        font-size: 0.85rem;
        display: inline-block;
    }

    .badge-cold {
        background: linear-gradient(135deg, rgba(141, 153, 174, 0.2) 0%, rgba(141, 153, 174, 0.35) 100%);
        border: 1px solid #8D99AE;
        color: #EDF2F4;
        padding: 4px 12px;
        border-radius: 20px;
        font-weight: 600;
        font-size: 0.85rem;
        display: inline-block;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #0077B6 0%, #0096C7 100%);
        color: #FFFFFF;
        border: none;
        border-radius: 8px;
        font-weight: 600;
        padding: 0.55rem 1.25rem;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #0096C7 0%, #48CAE4 100%);
        box-shadow: 0 4px 14px rgba(72, 202, 228, 0.35);
        color: #0B132B;
    }

    /* Input Fields */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #141C36 !important;
        color: #FFFFFF !important;
        border: 1px solid rgba(72, 202, 228, 0.25) !important;
        border-radius: 8px !important;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #48CAE4 !important;
        box-shadow: 0 0 0 2px rgba(72, 202, 228, 0.2) !important;
    }

    /* Dataframe Header */
    div[data-testid="stDataFrame"] {
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 10px;
        overflow: hidden;
    }

    /* Success / Info / Warning Alerts */
    div[data-baseweb="notification"] {
        background-color: #162244 !important;
        border-radius: 8px !important;
    }
</style>
"""

def apply_cynbit_theme():
    """Injects custom CSS styles into the current Streamlit page."""
    st.markdown(CYNBIT_CSS, unsafe_allow_html=True)
