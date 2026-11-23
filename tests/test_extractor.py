"""
Unit tests for Cynbit Customer Requirement & Entity Extractor.
"""

import pytest
from app.services.extractor_service import extractor_service

def test_extract_budget():
    # Explicit $45,000
    val, raw = extractor_service.extract_budget("Our total allocated budget is $45,000.")
    assert val == 45000.0
    assert "$45,000" in raw
    
    # Notation $35k
    val2, raw2 = extractor_service.extract_budget("We have roughly $35k set aside.")
    assert val2 == 35000.0
    
    # Flexible budget
    val3, raw3 = extractor_service.extract_budget("We have a flexible budget for the right team.")
    assert val3 == 30000.0
    assert "Flexible" in raw3
    
    # Unspecified
    val4, raw4 = extractor_service.extract_budget("Please send us your service catalog.")
    assert val4 is None
    assert raw4 == "Unspecified"

def test_extract_timeline():
    t1 = extractor_service.extract_timeline("We need this delivered within 2 months.")
    assert "2 months" in t1.lower()
    
    t2 = extractor_service.extract_timeline("Our urgent launch target is 6 weeks.")
    assert "6 weeks" in t2.lower()
    
    t3 = extractor_service.extract_timeline("Need an MVP built ASAP.")
    assert "immediate" in t3.lower()

def test_extract_urgency():
    u_high = extractor_service.extract_urgency("This is an urgent requirement needed ASAP.", "Immediate (< 1 month)")
    assert u_high == "High"
    
    u_med = extractor_service.extract_urgency("We are targeting a launch in 2 months.", "2 months")
    assert u_med == "Medium"
    
    u_low = extractor_service.extract_urgency("We are doing preliminary exploratory research for next year.", "Flexible")
    assert u_low == "Low"

def test_extract_technologies():
    text = "We want a mobile app built with Flutter and deployed on AWS with Stripe checkout and Docker containers."
    techs = extractor_service.extract_technical_entities(text)
    assert "Flutter" in techs
    assert "AWS" in techs
    assert "Stripe" in techs
    assert "Docker" in techs
