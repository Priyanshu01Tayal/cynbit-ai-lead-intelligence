"""
Unit tests for Cynbit ML Pipeline.
"""

import pytest
from app.ml.pipeline import clean_text, LeadClassificationPipeline

def test_clean_text():
    raw = "We're looking for an AI/ML developer to build models! Can't wait..."
    cleaned = clean_text(raw)
    assert "we are" in cleaned or "looking" in cleaned
    assert "!" not in cleaned
    assert "ai" in cleaned

def test_pipeline_prediction():
    pipeline = LeadClassificationPipeline()
    assert pipeline.is_loaded is True
    
    # Test AI/ML prediction
    ai_inquiry = "We need an engineer to build a custom computer vision defect detection model using deep learning."
    res = pipeline.predict(ai_inquiry)
    assert res["category"] == "AI/ML Development"
    assert res["confidence"] > 0.3
    assert "probabilities" in res
    assert len(res["probabilities"]) == 6
    
    # Test Cloud & DevOps prediction
    cloud_inquiry = "Looking for a cloud architect to migrate 40 VMs to AWS with Terraform, Kubernetes EKS, and CI/CD."
    res_cloud = pipeline.predict(cloud_inquiry)
    assert res_cloud["category"] == "Cloud & DevOps"
    assert res_cloud["confidence"] > 0.3
