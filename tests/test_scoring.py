"""
Unit tests for Cynbit Lead Scoring System.
"""

import pytest
from app.services.scoring_service import scoring_service

def test_hot_lead_scoring():
    res = scoring_service.calculate_score(
        service_category="AI/ML Development",
        budget_estimated=65000.0,
        budget_raw="$65,000",
        urgency_level="High",
        timeline_raw="6 weeks",
        extracted_requirements=["Real-time inference", "Computer vision model", "SOC 2"],
        detected_technologies=["AWS", "PyTorch", "Kubernetes"],
        inquiry_text="We have a high-priority enterprise computer vision requirement with 50ms latency SLA on assembly lines."
    )
    assert res["score"] >= 75
    assert res["priority"] == "Hot"
    assert "breakdown" in res
    assert len(res["reasons"]) >= 4

def test_cold_lead_scoring():
    res = scoring_service.calculate_score(
        service_category="Other",
        budget_estimated=2000.0,
        budget_raw="$2,000",
        urgency_level="Low",
        timeline_raw="Flexible",
        extracted_requirements=[],
        detected_technologies=[],
        inquiry_text="General pricing question"
    )
    assert res["score"] < 50
    assert res["priority"] == "Cold"
    assert "reasons" in res

def test_warm_lead_scoring():
    res = scoring_service.calculate_score(
        service_category="Web Development",
        budget_estimated=18000.0,
        budget_raw="$18,000",
        urgency_level="Medium",
        timeline_raw="2 months",
        extracted_requirements=["Client portal with Stripe"],
        detected_technologies=["React"],
        inquiry_text="We want to build a client portal with Stripe billing for our agency over the next 2 months."
    )
    assert 50 <= res["score"] < 75
    assert res["priority"] == "Warm"
