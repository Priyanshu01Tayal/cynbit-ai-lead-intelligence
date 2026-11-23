"""
Cynbit AI - Unit Tests for Frontend Pages and Routing
Verifies that all Streamlit page scripts run without syntax or import errors,
and interact correctly with the centralized CynbitAPIClient.
"""

import os
import sys
from unittest.mock import patch, MagicMock
import pytest

@pytest.fixture
def mock_api_client():
    mock = MagicMock()
    mock.base_url = "https://cynbit-ai-lead-intelligence.onrender.com"
    mock.get_health.return_value = {
        "status": "healthy",
        "database": "healthy",
        "lead_count": 48,
        "model_loaded": True,
        "environment": "production"
    }
    mock.get_analytics_summary.return_value = {
        "total_leads": 48,
        "hot_leads": 24,
        "warm_leads": 16,
        "cold_leads": 8,
        "avg_score": 69.9,
        "conversion_rate": 6.25,
        "pipeline_value_estimated": 1245000.0,
        "status_counts": {"New": 11, "Qualified": 11},
        "category_counts": {"AI/ML Development": 8},
        "priority_counts": {"Hot": 24, "Warm": 16, "Cold": 8}
    }
    mock.get_conversion_funnel.return_value = [
        {"stage": "Inquiries (New)", "cumulative_count": 48, "current_stage_count": 11, "conversion_pct": 100.0}
    ]
    mock.get_distributions.return_value = {
        "category_priority": {"AI/ML Development": {"Hot": 4, "Warm": 2, "Cold": 2}},
        "urgency_priority": {"High": {"Hot": 10, "Warm": 2, "Cold": 0}},
        "score_distribution": [85, 72, 40],
        "budget_tiers": {"< $10k": 4, "$10k-$25k": 14, "$25k-$50k": 28, "> $50k": 2}
    }
    mock.list_leads.return_value = [
        {
            "lead_id": "CYN-2026-001",
            "client_name": "Alexander Wright",
            "client_company": "Vanguard Dynamics Corp",
            "client_email": "a.wright@enterprise.com",
            "service_category": "AI/ML Development",
            "category_confidence": 0.94,
            "score": 88,
            "priority": "Hot",
            "budget_raw": "$45,000",
            "urgency_level": "High",
            "timeline_raw": "8 weeks",
            "customer_intent": "Computer Vision Defect Detection",
            "status": "New",
            "notes": "Test lead",
            "created_at": "2026-11-23T06:50:00",
            "score_breakdown": {
                "budget": {"score": 25, "max": 30},
                "urgency": {"score": 25, "max": 25},
                "requirements": {"score": 18, "max": 20},
                "timeline": {"score": 12, "max": 15},
                "relevance": {"score": 8, "max": 10}
            },
            "score_reasons": ["High budget alignment"],
            "suggested_response": "Dear Alexander..."
        }
    ]
    mock.get_lead.return_value = mock.list_leads.return_value[0]
    mock.get_metrics.return_value = {
        "overall": {"accuracy": 0.8542, "macro_f1": 0.8608, "macro_precision": 0.865, "macro_recall": 0.858},
        "test_samples": 48,
        "labels": ["AI/ML Development", "Web Development"],
        "confusion_matrix": [[8, 0], [0, 8]],
        "per_class": {
            "AI/ML Development": {"precision": 1.0, "recall": 1.0, "f1_score": 1.0, "support": 8}
        },
        "top_features": {
            "AI/ML Development": [{"feature": "computer vision", "weight": 2.45}]
        }
    }
    return mock

def run_streamlit_page_script(filepath: str, mock_client):
    """Executes a page script with mocked streamlit session state and API client."""
    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    # Pre-populate session state
    import streamlit as st
    st.session_state.clear()
    
    with patch("frontend.utils.api_client.api_client", mock_client), \
         patch("frontend.components.sidebar.api_client", mock_client):
        # Compile and execute within a safe namespace
        namespace = {"__file__": filepath, "__name__": "__main__"}
        # Avoid streamlit set_page_config collision in unit tests
        with patch("streamlit.set_page_config"), \
             patch("streamlit.rerun"):
            exec(code, namespace)

def test_page_1_dashboard(mock_api_client):
    run_streamlit_page_script("frontend/pages/1_Dashboard.py", mock_api_client)
    assert mock_api_client.get_analytics_summary.called
    assert mock_api_client.get_conversion_funnel.called
    assert mock_api_client.list_leads.called

def test_page_2_add_new_lead(mock_api_client):
    run_streamlit_page_script("frontend/pages/2_Add_New_Lead.py", mock_api_client)

def test_page_3_lead_management(mock_api_client):
    run_streamlit_page_script("frontend/pages/3_Lead_Management.py", mock_api_client)
    assert mock_api_client.list_leads.called

def test_page_4_lead_intelligence(mock_api_client):
    run_streamlit_page_script("frontend/pages/4_Lead_Intelligence.py", mock_api_client)
    assert mock_api_client.get_lead.called

def test_page_5_analytics(mock_api_client):
    run_streamlit_page_script("frontend/pages/5_Analytics.py", mock_api_client)
    assert mock_api_client.get_distributions.called

def test_page_6_model_performance(mock_api_client):
    run_streamlit_page_script("frontend/pages/6_Model_Performance.py", mock_api_client)
    assert mock_api_client.get_metrics.called

def test_page_7_about_project(mock_api_client):
    run_streamlit_page_script("frontend/pages/7_About_Project.py", mock_api_client)
