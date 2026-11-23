"""
Cynbit AI - Streamlit Reusable UI Cards & Badges
"""

import streamlit as st

def render_kpi_card(title: str, value: str, subtext: str = "", border_color: str = "#3A86FF"):
    """Renders a styled KPI metric card."""
    st.markdown(f"""
    <div class="cynbit-kpi-card" style="border-left: 4px solid {border_color};">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
        {f'<div class="kpi-subtext">{subtext}</div>' if subtext else ''}
    </div>
    """, unsafe_allow_html=True)

def render_priority_badge(priority: str) -> str:
    """Returns HTML for color-coded priority badge."""
    p_lower = priority.lower()
    if p_lower == "hot":
        return '<span class="badge-hot">🔥 Hot Lead</span>'
    elif p_lower == "warm":
        return '<span class="badge-warm">⚡ Warm Lead</span>'
    else:
        return '<span class="badge-cold">❄️ Cold Lead</span>'

def render_score_badge(score: int) -> str:
    """Returns HTML score pill with dynamic color."""
    if score >= 75:
        color = "#EF476F"
        bg = "rgba(239, 71, 111, 0.2)"
    elif score >= 50:
        color = "#FFB703"
        bg = "rgba(255, 183, 3, 0.2)"
    else:
        color = "#8D99AE"
        bg = "rgba(141, 153, 174, 0.2)"
        
    return f"""
    <div style="display: inline-block; background-color: {bg}; border: 1px solid {color}; border-radius: 8px; padding: 4px 10px; font-weight: 800; font-family: monospace; color: {color};">
        {score} / 100
    </div>
    """
