"""
Cynbit AI - Lead Scoring System
Calculates a 0-100 multidimensional score and priority tier (Hot, Warm, Cold)
with explainable factor breakdown and actionable sales recommendations.
"""

from typing import Dict, Any, List, Optional

class LeadScoringService:
    """Calculates multidimensional qualification scores with explainable justifications."""
    
    HOT_THRESHOLD = 75
    WARM_THRESHOLD = 50
    
    def calculate_score(
        self,
        service_category: str,
        budget_estimated: Optional[float],
        budget_raw: str,
        urgency_level: str,
        timeline_raw: str,
        extracted_requirements: List[str],
        detected_technologies: List[str],
        inquiry_text: str
    ) -> Dict[str, Any]:
        """
        Computes composite score across:
        - Budget (0-30)
        - Urgency (0-25)
        - Requirements Clarity (0-20)
        - Timeline Feasibility (0-15)
        - Service Relevance (0-10)
        """
        reasons = []
        breakdown = {}
        
        # 1. Budget Score (0-30 pts)
        budget_score = 0
        if budget_estimated is not None and budget_estimated > 0:
            if budget_estimated >= 50000:
                budget_score = 30
                reasons.append(f"Enterprise-grade budget ({budget_raw}): High commercial contract value.")
            elif budget_estimated >= 25000:
                budget_score = 25
                reasons.append(f"Strong mid-market budget ({budget_raw}): Well-aligned with Cynbit project averages.")
            elif budget_estimated >= 10000:
                budget_score = 18
                reasons.append(f"Standard commercial budget ({budget_raw}): Suitable for focused MVP / phase 1 delivery.")
            elif budget_estimated >= 5000:
                budget_score = 10
                reasons.append(f"Modest budget ({budget_raw}): May require scope adjustment or phased delivery.")
            else:
                budget_score = 2
                reasons.append(f"Sub-threshold budget ({budget_raw}): Below standard agency minimum engagement.")
        else:
            if "flexible" in budget_raw.lower() or "enterprise" in budget_raw.lower():
                budget_score = 16
                reasons.append("Flexible budget indicated: Requires early commercial alignment in discovery.")
            else:
                budget_score = 12
                reasons.append("Budget not explicitly stated: Requires qualification call to establish financial fit.")
        breakdown["budget"] = {"score": budget_score, "max": 30, "weight_pct": 30}

        # 2. Urgency Score (0-25 pts)
        urgency_score = 0
        urgency_lower = urgency_level.lower()
        if urgency_lower == "high":
            urgency_score = 25
            reasons.append("High project urgency: Active buying window; rapid sales response required.")
        elif urgency_lower == "medium":
            urgency_score = 17
            reasons.append("Medium project urgency: Standard procurement timeframe (1-2 months).")
        else:
            urgency_score = 8
            reasons.append("Low project urgency: Exploratory or long-cycle planning phase.")
        breakdown["urgency"] = {"score": urgency_score, "max": 25, "weight_pct": 25}

        # 3. Requirements Clarity (0-20 pts)
        req_score = 0
        text_words = len(inquiry_text.split())
        tech_count = len(detected_technologies)
        req_count = len(extracted_requirements)
        
        if (tech_count >= 2 or req_count >= 3) and text_words >= 30:
            req_score = 20
            reasons.append("Highly articulated scope: Client has well-defined technical specifications and stack requirements.")
        elif text_words >= 15 or tech_count >= 1:
            req_score = 14
            reasons.append("Moderate requirement clarity: Clear business objective identified with core scope points.")
        else:
            req_score = 6
            reasons.append("Brief / vague inquiry: Lacks technical depth; requires extensive scoping discovery.")
        breakdown["requirements"] = {"score": req_score, "max": 20, "weight_pct": 20}

        # 4. Timeline Feasibility (0-15 pts)
        timeline_score = 0
        timeline_lower = timeline_raw.lower()
        if any(w in timeline_lower for w in ["month", "weeks", "quarter", "q1", "q2", "q3", "q4"]):
            if any(w in timeline_lower for w in ["1 week", "2 days", "3 days"]):
                timeline_score = 6
                reasons.append(f"Extremely tight timeline ({timeline_raw}): Potential delivery risk without pre-built modules.")
            else:
                timeline_score = 15
                reasons.append(f"Realistic project timeline ({timeline_raw}): Allows standard sprint planning and QA.")
        elif "immediate" in timeline_lower or "asap" in timeline_lower:
            timeline_score = 12
            reasons.append(f"Accelerated timeline ({timeline_raw}): High buyer intent, needs immediate resource allocation.")
        else:
            timeline_score = 8
            reasons.append(f"Unspecified or open-ended timeline ({timeline_raw}): Milestones to be defined during scoping.")
        breakdown["timeline"] = {"score": timeline_score, "max": 15, "weight_pct": 15}

        # 5. Service Relevance (0-10 pts)
        relevance_score = 0
        high_relevance_services = ["AI/ML Development", "Cloud & DevOps", "Business Automation"]
        core_services = ["Web Development", "Mobile App Development"]
        
        if service_category in high_relevance_services:
            relevance_score = 10
            reasons.append(f"Core strategic competency ({service_category}): High-margin specialization for Cynbit.")
        elif service_category in core_services:
            relevance_score = 8
            reasons.append(f"Standard core service ({service_category}): Consistent demand and delivery capability.")
        else:
            relevance_score = 4
            reasons.append(f"Peripheral or non-core inquiry ({service_category}): Requires verification of capabilities.")
        breakdown["relevance"] = {"score": relevance_score, "max": 10, "weight_pct": 10}

        # Composite Score
        total_score = budget_score + urgency_score + req_score + timeline_score + relevance_score
        total_score = max(0, min(100, total_score))

        # Classification into Priority Tier
        if total_score >= self.HOT_THRESHOLD:
            priority = "Hot"
            action_recommendation = "Immediate priority: Schedule executive discovery call within 4 hours. Prepare custom technical proposal."
        elif total_score >= self.WARM_THRESHOLD:
            priority = "Warm"
            action_recommendation = "Nurture lead: Dispatch Cynbit capabilities deck & portfolio case study within 24 hours. Propose scoping workshop."
        else:
            priority = "Cold"
            action_recommendation = "Low priority / Automated nurturing: Send qualification questionnaire and general pricing guide."

        return {
            "score": total_score,
            "priority": priority,
            "breakdown": breakdown,
            "reasons": reasons,
            "action_recommendation": action_recommendation
        }

# Global singleton
scoring_service = LeadScoringService()
