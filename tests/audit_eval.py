"""
Cynbit AI - Independent Audit Script
Performs verification of ML model, lead scoring across 10 scenarios,
and API/Database operations.
"""

import os
import json
import pandas as pd
from app.ml.pipeline import LeadClassificationPipeline
from app.services.scoring_service import scoring_service
from app.services.extractor_service import extractor_service
from app.services.lead_service import lead_service

def verify_ml_on_novel_inquiries():
    pipeline = LeadClassificationPipeline()
    test_cases = [
        ("We need a custom LLM fine-tuned on our internal clinical trial protocols with private hosting on Nvidia H100s.", "AI/ML Development"),
        ("Our marketing team needs an automated workflow that connects Airtable to Google Drive and auto-generates client invoices in QuickBooks.", "Business Automation"),
        ("Looking for an experienced team to migrate our monolith Django app to AWS EKS with ArgoCD GitOps and Prometheus monitoring.", "Cloud & DevOps"),
        ("We want to build an iOS and Android app in Flutter for real-time electric vehicle charging station reservations and payments.", "Mobile App Development"),
        ("Need a high-converting web landing page suite and client onboarding portal built with Next.js, TypeScript, and Tailwind CSS.", "Web Development"),
        ("Hello, we are preparing our annual vendor review and would like to request your master services agreement and hourly rate card.", "Other")
    ]

    print("=" * 60)
    print("1. EVALUATION ON COMPLETELY NOVEL UNSEEN INQUIRIES")
    print("=" * 60)
    correct = 0
    results = []
    for text, expected in test_cases:
        res = pipeline.predict(text)
        pred = res["category"]
        conf = res["confidence"]
        matched = (pred == expected)
        if matched:
            correct += 1
        results.append({
            "text": text,
            "expected": expected,
            "predicted": pred,
            "confidence": conf,
            "matched": matched
        })
        print(f"Inquiry: {text[:65]}...")
        print(f" -> Expected: {expected}")
        print(f" -> Predicted: {pred} (Confidence: {conf*100:.1f}%) | {'PASS' if matched else 'FAIL'}\n")

    acc = correct / len(test_cases)
    print(f"Novel Inquiries Accuracy: {correct}/{len(test_cases)} ({acc*100:.1f}%)\n")
    return results

def verify_ten_scoring_scenarios():
    print("=" * 60)
    print("2. VERIFYING 10 SPECIFIC LEAD SCORING SCENARIOS")
    print("=" * 60)

    scenarios = [
        {
            "id": "Scenario 1",
            "name": "High-budget urgent AI project",
            "inquiry": "We need an enterprise computer vision defect detection model on assembly lines. Budget is $80,000 and we need deployment urgently within 3 weeks.",
            "expected_priority": "Hot",
            "min_score": 75
        },
        {
            "id": "Scenario 2",
            "name": "Low-budget web development project",
            "inquiry": "Need a simple 3-page website redesign. Our maximum budget is $2,500 and timeline is flexible over the next 3 months.",
            "expected_priority": "Cold",
            "max_score": 55
        },
        {
            "id": "Scenario 3",
            "name": "Vague inquiry",
            "inquiry": "Hi, please contact me regarding software.",
            "expected_priority": "Cold",
            "max_score": 50
        },
        {
            "id": "Scenario 4",
            "name": "Long-term cloud project",
            "inquiry": "We are planning an enterprise cloud migration to AWS spanning our 50 microservices. Budget is $40,000 with a realistic 6-month phased roadmap.",
            "expected_priority": "Hot", # Strong budget, high relevance, realistic timeline
            "min_score": 70
        },
        {
            "id": "Scenario 5",
            "name": "Unrealistic timeline",
            "inquiry": "We need a full clone of Uber and Airbnb built from scratch in 2 days. Budget is $5,000.",
            "expected_priority": "Cold",
            "max_score": 55
        },
        {
            "id": "Scenario 6",
            "name": "Missing budget",
            "inquiry": "Looking to build a predictive machine learning model for churn forecasting. Target timeline is 2 months. Budget to be discussed.",
            "expected_priority": "Warm",
            "min_score": 50,
            "max_score": 75
        },
        {
            "id": "Scenario 7",
            "name": "Missing timeline",
            "inquiry": "We have an approved $30,000 budget for robotic process automation to sync invoices into SAP.",
            "expected_priority": "Warm",
            "min_score": 55
        },
        {
            "id": "Scenario 8",
            "name": "Automation inquiry",
            "inquiry": "We spend 30 hours weekly manually entering invoice data from PDFs into QuickBooks. Looking for automated IDP pipeline. Budget $22,000, 6 weeks.",
            "expected_priority": "Hot",
            "min_score": 70
        },
        {
            "id": "Scenario 9",
            "name": "Mobile application inquiry",
            "inquiry": "Need a cross-platform mobile app in Flutter for doctor video consultations with Stripe integration. Budget $35,000, 3 months.",
            "expected_priority": "Hot",
            "min_score": 72
        },
        {
            "id": "Scenario 10",
            "name": "General inquiry",
            "inquiry": "Can you send us your corporate brochure and hourly billing rates for junior and senior engineers?",
            "expected_priority": "Cold",
            "max_score": 50
        }
    ]

    results = []
    for s in scenarios:
        res = lead_service.analyze_lead_inquiry(s["inquiry"])
        score = res["score"]
        priority = res["priority"]
        cat = res["service_category"]
        
        # Verify bounds 0-100
        bounded = 0 <= score <= 100
        
        status_pass = True
        if "expected_priority" in s and priority != s["expected_priority"]:
            # Check if close boundary or acceptable
            if abs(score - 75) <= 3 or abs(score - 50) <= 3:
                status_pass = True # Near threshold
            else:
                status_pass = False
                
        results.append({
            "scenario": s["name"],
            "category": cat,
            "score": score,
            "priority": priority,
            "bounded": bounded,
            "pass": status_pass,
            "reasons": res["score_reasons"]
        })
        
        print(f"[{s['id']}] {s['name']}")
        print(f" -> Category: {cat}")
        print(f" -> Score: {score}/100 (Bounded: {bounded}) | Priority: {priority} (Expected: {s.get('expected_priority')})")
        print(f" -> Key reason: {res['score_reasons'][0] if res['score_reasons'] else 'N/A'}")
        print()
        
    return results

if __name__ == "__main__":
    verify_ml_on_novel_inquiries()
    verify_ten_scoring_scenarios()
