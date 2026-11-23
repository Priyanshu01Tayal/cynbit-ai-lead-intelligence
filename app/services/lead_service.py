"""
Cynbit AI - Core Lead Orchestration Service
Coordinates NLP classification, entity extraction, multidimensional scoring,
and response generation into a single unified analysis result.
"""

import json
from typing import Dict, Any, Optional

from app.ml.pipeline import LeadClassificationPipeline
from app.services.extractor_service import extractor_service
from app.services.scoring_service import scoring_service
from app.services.response_service import response_service

class LeadService:
    """Unified orchestration service for lead intelligence."""
    
    def __init__(self):
        self.ml_pipeline = LeadClassificationPipeline()
        self.extractor = extractor_service
        self.scorer = scoring_service
        self.response_gen = response_service
        
    def reload_model(self):
        """Reloads the classification model from disk after training."""
        self.ml_pipeline = LeadClassificationPipeline()
        
    def analyze_lead_inquiry(
        self,
        inquiry_text: str,
        client_name: str = "",
        client_email: str = "",
        client_company: str = "",
        manual_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        End-to-end lead analysis:
        1. Classify service category with ML pipeline (or manual override).
        2. Extract customer requirements, budget, timeline, urgency, intent.
        3. Compute 0-100 multidimensional lead score & priority tier (Hot/Warm/Cold).
        4. Generate contextual, personalized business response.
        """
        # 1. ML Classification
        ml_result = self.ml_pipeline.predict(inquiry_text)
        service_category = manual_category if manual_category else ml_result["category"]
        category_confidence = ml_result["confidence"]
        
        # 2. Entity & Requirement Extraction
        extracted = self.extractor.analyze_inquiry(inquiry_text)
        
        # 3. Scoring System
        scoring_result = self.scorer.calculate_score(
            service_category=service_category,
            budget_estimated=extracted["budget_estimated"],
            budget_raw=extracted["budget_raw"],
            urgency_level=extracted["urgency_level"],
            timeline_raw=extracted["timeline_raw"],
            extracted_requirements=extracted["extracted_requirements"],
            detected_technologies=extracted["detected_technologies"],
            inquiry_text=inquiry_text
        )
        
        # 4. Response Generation
        response_result = self.response_gen.generate_response(
            client_name=client_name,
            client_company=client_company,
            inquiry_text=inquiry_text,
            service_category=service_category,
            budget_raw=extracted["budget_raw"],
            timeline_raw=extracted["timeline_raw"],
            priority=scoring_result["priority"],
            score=scoring_result["score"],
            detected_technologies=extracted["detected_technologies"],
            customer_intent=extracted["customer_intent"]
        )
        
        return {
            "client_name": client_name,
            "client_email": client_email,
            "client_company": client_company,
            "inquiry_text": inquiry_text,
            "service_category": service_category,
            "category_confidence": category_confidence,
            "classification_details": ml_result,
            "customer_intent": extracted["customer_intent"],
            "detected_technologies": extracted["detected_technologies"],
            "extracted_requirements": extracted["extracted_requirements"],
            "budget_estimated": extracted["budget_estimated"],
            "budget_raw": extracted["budget_raw"],
            "timeline_raw": extracted["timeline_raw"],
            "urgency_level": extracted["urgency_level"],
            "score": scoring_result["score"],
            "priority": scoring_result["priority"],
            "score_breakdown": scoring_result["breakdown"],
            "score_reasons": scoring_result["reasons"],
            "action_recommendation": scoring_result["action_recommendation"],
            "suggested_response": response_result["response_text"],
            "response_engine": response_result["engine"]
        }

# Global singleton
lead_service = LeadService()
