"""
Integration and endpoint tests for Cynbit FastAPI Backend Routes.
"""

import pytest
from app.database import SessionLocal, init_db
from app.main import health_check
from app.routes.leads import analyze_inquiry, create_lead, get_lead, update_lead, list_leads
from app.routes.analytics import get_analytics_summary, get_conversion_funnel
from app.routes.ml import get_metrics
from app.schemas.lead import (
    LeadAnalyzeRequest,
    LeadCreateRequest,
    LeadUpdateRequest
)

@pytest.fixture(scope="module")
def db_session():
    init_db()
    db = SessionLocal()
    yield db
    db.close()

def test_health_check_endpoint():
    res = health_check()
    assert res["status"] == "healthy"
    assert "lead_count" in res
    assert res["lead_count"] >= 40
    assert res["model_loaded"] is True

def test_analyze_lead_endpoint():
    req = LeadAnalyzeRequest(
        inquiry_text="We need an AI/ML engineer to build a predictive customer churn model with PostgreSQL integration. Budget is $30,000 and deadline is 2 months.",
        client_name="Test Client",
        client_company="Acme Corp"
    )
    res = analyze_inquiry(req)
    assert res["service_category"] == "AI/ML Development"
    assert res["score"] >= 65
    assert res["priority"] in ["Hot", "Warm"]
    assert "suggested_response" in res
    assert len(res["suggested_response"]) > 50

def test_create_and_manage_lead(db_session):
    # 1. Create Lead
    req = LeadCreateRequest(
        inquiry_text="Looking for a cloud specialist to implement AWS CI/CD pipelines and Kubernetes cluster. Budget $25,000, 6 weeks.",
        client_name="DevOps Lead",
        client_email="devops@cloudtest.com",
        client_company="CloudTest Inc",
        notes="Met at tech symposium"
    )
    created = create_lead(req, db=db_session)
    lead_id = created["lead_id"]
    assert lead_id.startswith("CYN-2026-")
    assert created["service_category"] == "Cloud & DevOps"
    assert created["status"] == "New"
    
    # 2. Get Lead by ID
    fetched = get_lead(lead_id, db=db_session)
    assert fetched["client_company"] == "CloudTest Inc"
    assert fetched["score"] > 50
    
    # 3. Update Lead Status
    update_req = LeadUpdateRequest(status="Contacted", notes="Emailed technical architecture deck")
    updated = update_lead(lead_id, update_req, db=db_session)
    assert updated["status"] == "Contacted"
    assert "technical architecture deck" in updated["notes"]
    
    # 4. List Leads with Filter
    filtered_leads = list_leads(category="Cloud & DevOps", db=db_session)
    assert len(filtered_leads) >= 1
    assert all(l["service_category"] == "Cloud & DevOps" for l in filtered_leads)

def test_analytics_endpoints(db_session):
    summary = get_analytics_summary(db=db_session)
    assert summary["total_leads"] >= 40
    assert summary["hot_leads"] > 0
    assert summary["warm_leads"] > 0
    assert summary["pipeline_value_estimated"] > 0
    
    funnel = get_conversion_funnel(db=db_session)
    assert len(funnel) == 6
    assert funnel[0]["stage"] == "Inquiries (New)"
    assert funnel[0]["cumulative_count"] >= summary["total_leads"]

def test_ml_metrics_endpoint():
    metrics = get_metrics()
    assert "overall" in metrics
    assert "accuracy" in metrics["overall"]
    assert metrics["overall"]["accuracy"] > 0.70
    assert "confusion_matrix" in metrics
    assert "per_class" in metrics
    assert "top_features" in metrics
