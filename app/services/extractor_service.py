"""
Cynbit AI - Customer Requirement & Entity Extractor Service
Extracts budget, timeline, urgency, intent, and technical requirements from unstructured inquiry text.
"""

import re
from typing import Dict, Any, List, Optional, Tuple

class EntityExtractorService:
    """Intelligent entity and requirement extractor using contextual regex and semantic patterns."""
    
    # Currency and budget pattern matching
    BUDGET_PATTERNS = [
        # $45,000 or $45k or $45.5k or $45000
        r"\$\s*([0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?|\d+(?:\.\d+)?)\s*(k|m|million|thousand)?\b",
        # 45k usd / 45,000 usd
        r"\b([0-9]{1,3}(?:,[0-9]{3})*|\d+)\s*(k|m|thousand|million)?\s*(?:usd|dollars|eur|euros|inr|gbp)\b",
        # budget of / budget is 35000 / 35k
        r"(?:budget|cost|price|range)(?:\s*(?:is|of|around|approx|approximately|:|about))?\s*(?:up\s*to|under|around)?\s*\$?\s*([0-9]{1,3}(?:,[0-9]{3})*|\d+)\s*(k|m|thousand|million)?\b"
    ]
    
    TIMELINE_PATTERNS = [
        r"\b(\d+\s*(?:to|-)\s*\d+\s*(?:days?|weeks?|months?|quarters?))\b",
        r"\b(\d+\s*(?:days?|weeks?|months?))\b",
        r"\b(within\s*(?:a|\d+)?\s*(?:few\s*)?(?:days?|weeks?|months?))\b",
        r"\b(q[1-4](?:\s*202[4-9])?)\b",
        r"\b(asap|immediately|immediate|urgent|next\s*quarter|next\s*year)\b"
    ]
    
    HIGH_URGENCY_KEYWORDS = [
        "urgent", "urgently", "asap", "immediate", "immediately", "critical", 
        "emergency", "fast-track", "rush", "1 week", "2 weeks", "10 days", "within a week"
    ]
    
    MEDIUM_URGENCY_KEYWORDS = [
        "soon", "month", "1 month", "2 months", "6 weeks", "8 weeks", "q1", "q2", "q3", "q4", 
        "upcoming", "weeks", "shortly"
    ]
    
    INTENT_MAP = {
        "New Product Development": [
            "build", "develop", "create", "launch", "mvp", "prototype", "new", "from scratch", "greenfield"
        ],
        "System Modernization & Migration": [
            "migrate", "migration", "rebuild", "modernize", "refactor", "transition", "replace legacy", "upgrade"
        ],
        "Performance & Cost Optimization": [
            "optimize", "optimization", "reduce cost", "finops", "latency", "scale", "bottleneck", "audit"
        ],
        "Process Automation & Integration": [
            "automate", "automation", "workflow", "sync", "integrate", "integration", "pipeline", "rpa"
        ],
        "Security & Compliance Audit": [
            "soc 2", "hipaa", "security", "audit", "compliance", "penetration", "vulnerability", "gdpr"
        ],
        "Advisory & General Consulting": [
            "consulting", "advisory", "pricing", "brochure", "guidelines", "rates", "internship", "partner"
        ]
    }
    
    KNOWN_TECH_ENTITIES = [
        "AWS", "GCP", "Google Cloud", "Azure", "Kubernetes", "Docker", "Terraform", "Python", 
        "React", "Next.js", "Flutter", "iOS", "Android", "Swift", "Kotlin", "React Native",
        "OpenAI", "Llama", "RAG", "PostgreSQL", "MySQL", "MongoDB", "Redis", "Kafka", "Elasticsearch",
        "HubSpot", "Salesforce", "Shopify", "Stripe", "Twilio", "Epic EHR", "HIPAA", "SOC 2",
        "GitLab", "GitHub", "ArgoCD", "Prometheus", "Grafana", "Make", "n8n", "Zapier", "Pinecone"
    ]

    def extract_budget(self, text: str) -> Tuple[Optional[float], str]:
        """Extracts estimated numerical budget and raw display string."""
        text_lower = text.lower()
        
        # Check explicit patterns
        for pattern in self.BUDGET_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                raw_val = match.group(1).replace(",", "")
                unit = match.group(2) if len(match.groups()) > 1 else None
                try:
                    val = float(raw_val)
                    if unit in ("k", "thousand"):
                        val *= 1000
                    elif unit in ("m", "million"):
                        val *= 1000000
                    return round(val, 2), f"${val:,.0f}"
                except ValueError:
                    continue
                    
        # Check qualitative budget hints
        if any(w in text_lower for w in ["flexible budget", "budget is flexible", "open budget"]):
            return 30000.0, "Flexible (Estimated ~$30k)"
        if any(w in text_lower for w in ["enterprise", "large budget", "well funded"]):
            return 50000.0, "Enterprise Grade (> $50k)"
            
        return None, "Unspecified"

    def extract_timeline(self, text: str) -> str:
        """Extracts timeline information from inquiry text."""
        text_lower = text.lower()
        for pattern in self.TIMELINE_PATTERNS:
            match = re.search(pattern, text_lower)
            if match:
                matched_str = match.group(1).strip()
                if matched_str in ("asap", "immediately", "immediate", "urgent"):
                    return "Immediate (< 1 month)"
                return matched_str.capitalize()
                
        if "asap" in text_lower or "immediate" in text_lower:
            return "Immediate (< 1 month)"
            
        return "Flexible / Not Stated"

    def extract_urgency(self, text: str, timeline: str) -> str:
        """Determines urgency level: High, Medium, or Low."""
        text_lower = text.lower()
        
        # Explicit low urgency overrides
        if any(w in text_lower for w in ["flexible", "no rush", "exploratory", "next year", "no hurry"]):
            return "Low"
            
        for kw in self.HIGH_URGENCY_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                return "High"
                
        if "immediate" in timeline.lower() or "week" in timeline.lower():
            return "High"
            
        for kw in self.MEDIUM_URGENCY_KEYWORDS:
            if re.search(r"\b" + re.escape(kw) + r"\b", text_lower):
                return "Medium"
                
        if "month" in timeline.lower():
            return "Medium"
            
        return "Low"

    def extract_intent(self, text: str) -> str:
        """Identifies customer business intent."""
        text_lower = text.lower()
        scores = {}
        for intent, kws in self.INTENT_MAP.items():
            count = sum(1 for kw in kws if kw in text_lower)
            scores[intent] = count
            
        best_intent = max(scores, key=scores.get)
        if scores[best_intent] > 0:
            return best_intent
        return "General Exploration / Scoping"

    def extract_technical_entities(self, text: str) -> List[str]:
        """Identifies mentions of known technologies, platforms, and compliance standards."""
        detected = []
        for tech in self.KNOWN_TECH_ENTITIES:
            # Word boundary check case-insensitively
            if re.search(r"\b" + re.escape(tech.lower()) + r"\b", text.lower()):
                detected.append(tech)
        return detected

    def extract_requirements_summary(self, text: str, tech_entities: List[str], intent: str) -> List[str]:
        """Summarizes key technical and business requirements."""
        reqs = []
        
        # Add tech stack detected
        if tech_entities:
            reqs.append(f"Target Technologies & Frameworks: {', '.join(tech_entities)}")
            
        # Add intent
        reqs.append(f"Primary Objective: {intent}")
        
        # Check specific constraints
        text_lower = text.lower()
        if "hipaa" in text_lower:
            reqs.append("Compliance: Strict HIPAA healthcare security & patient data privacy")
        if "soc 2" in text_lower:
            reqs.append("Compliance: SOC 2 Type II audit trail & access controls")
        if "latency" in text_lower or "ms" in text_lower:
            reqs.append("Performance: Low-latency SLA (< 100ms response time requirement)")
        if "offline" in text_lower:
            reqs.append("Capability: Offline-first data caching and sync")
        if "multi-tenant" in text_lower:
            reqs.append("Architecture: Secure multi-tenant data isolation")
        if "real-time" in text_lower or "websockets" in text_lower:
            reqs.append("Architecture: Real-time bi-directional streaming/updates")
            
        if len(reqs) <= 2:
            # Extract first substantive sentence as scope
            sentences = [s.strip() for s in re.split(r"[.!?]", text) if len(s.strip()) > 15]
            if sentences:
                reqs.append(f"Scope Summary: {sentences[0]}")
                
        return reqs

    def analyze_inquiry(self, text: str) -> Dict[str, Any]:
        """Full entity and requirement analysis pipeline."""
        budget_est, budget_raw = self.extract_budget(text)
        timeline = self.extract_timeline(text)
        urgency = self.extract_urgency(text, timeline)
        intent = self.extract_intent(text)
        tech_entities = self.extract_technical_entities(text)
        requirements = self.extract_requirements_summary(text, tech_entities, intent)
        
        return {
            "budget_estimated": budget_est,
            "budget_raw": budget_raw,
            "timeline_raw": timeline,
            "urgency_level": urgency,
            "customer_intent": intent,
            "detected_technologies": tech_entities,
            "extracted_requirements": requirements
        }

# Global singleton
extractor_service = EntityExtractorService()
