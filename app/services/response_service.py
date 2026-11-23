"""
Cynbit AI - Automated Business Response Generator
Generates personalized, professional client responses based on inquiry details,
service category, budget, timeline, and lead priority.
Supports LLM API (Gemini/OpenAI) if configured, with high-quality deterministic fallback.
"""

import os
import requests
from typing import Dict, Any, Optional

class ResponseGeneratorService:
    """Generates context-rich, conversion-optimized business responses."""
    
    def generate_response(
        self,
        client_name: str,
        client_company: str,
        inquiry_text: str,
        service_category: str,
        budget_raw: str,
        timeline_raw: str,
        priority: str,
        score: int,
        detected_technologies: list,
        customer_intent: str
    ) -> Dict[str, Any]:
        """Generates response using LLM if available, else deterministic template."""
        client_display = client_name.strip() if client_name and client_name.strip() else "Valued Partner"
        company_display = f" at {client_company.strip()}" if client_company and client_company.strip() else ""
        
        # Check if LLM API is available and configured
        gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
        openai_api_key = os.getenv("OPENAI_API_KEY", "").strip()
        
        if gemini_api_key:
            llm_resp = self._call_gemini_api(
                gemini_api_key, client_display, company_display, inquiry_text,
                service_category, budget_raw, timeline_raw, priority, detected_technologies
            )
            if llm_resp:
                return {
                    "response_text": llm_resp,
                    "engine": "Gemini-Pro LLM (Live API)",
                    "is_fallback": False
                }
                
        # Deterministic high-quality template engine
        template_resp = self._build_template_response(
            client_display, company_display, inquiry_text, service_category,
            budget_raw, timeline_raw, priority, score, detected_technologies, customer_intent
        )
        return {
            "response_text": template_resp,
            "engine": "Cynbit Expert Rule & Template Engine",
            "is_fallback": True
        }

    def _build_template_response(
        self,
        client_display: str,
        company_display: str,
        inquiry_text: str,
        service_category: str,
        budget_raw: str,
        timeline_raw: str,
        priority: str,
        score: int,
        detected_technologies: list,
        customer_intent: str
    ) -> str:
        """Constructs an executive-grade customized proposal email."""
        
        # Category-specific technical opening
        cat_intros = {
            "AI/ML Development": (
                "Our AI & Machine Learning Practice has helped enterprise and growth clients design, "
                "train, and deploy resilient models—from custom computer vision and NLP to fine-tuned LLMs "
                "and production inference microservices."
            ),
            "Web Development": (
                "Our Full-Stack Web Engineering team specializes in building high-performance, scalable web "
                "applications using modern architectures (Next.js, React, Python/Node microservices) with a strong "
                "focus on Core Web Vitals, conversion, and enterprise security."
            ),
            "Mobile App Development": (
                "Our Mobile Engineering team delivers native (Swift, Kotlin) and cross-platform (Flutter, React Native) "
                "applications that combine fluid, 60fps user experiences with robust backend integrations and offline reliability."
            ),
            "Cloud & DevOps": (
                "Our Cloud & Platform Engineering Practice specializes in enterprise cloud migrations (AWS, Azure, GCP), "
                "Kubernetes orchestration, infrastructure-as-code (Terraform), and automated CI/CD pipelines with SOC 2 compliance."
            ),
            "Business Automation": (
                "Our Intelligent Automation team focuses on eliminating manual operational bottlenecks through "
                "intelligent document processing, custom API integrations, and event-driven workflow automation."
            ),
            "Other": (
                "Our Technology Advisory Practice works closely with executive leaders on technology architecture "
                "evaluations, strategic modernization roadmaps, and custom engineering engagements."
            )
        }
        
        intro_paragraph = cat_intros.get(service_category, cat_intros["Other"])
        tech_mention = ""
        if detected_technologies:
            tech_mention = f"We noted your focus on {', '.join(detected_technologies[:4])}, which directly aligns with our core technical stack."

        # Commercial and Timeline acknowledgment
        commercial_notes = []
        if budget_raw and budget_raw != "Unspecified":
            commercial_notes.append(f"budget parameters ({budget_raw})")
        if timeline_raw and timeline_raw != "Flexible / Not Stated":
            commercial_notes.append(f"targeted timeframe ({timeline_raw})")
            
        comm_sentence = ""
        if commercial_notes:
            comm_sentence = f"We have factored your {' and '.join(commercial_notes)} into our initial scoping assessment to ensure delivery feasibility."

        # Strategic Call-to-Action based on Priority
        if priority == "Hot":
            cta_block = (
                "Given the high strategic priority and urgency of this initiative, we would like to offer you an "
                "exclusive 45-minute Technical Architecture Discovery Session with our Principal Solutions Architect this week.\n\n"
                "During this session, we will:\n"
                "1. Map your requirements to an optimal solution architecture.\n"
                "2. Provide an indicative Sprint Plan & Milestone Roadmap.\n"
                "3. Review mutual NDAs and team staffing availability."
            )
        elif priority == "Warm":
            cta_block = (
                "To help you evaluate our capabilities for this project, we would be pleased to share our curated "
                "Capabilities Deck and relevant Case Studies in this domain.\n\n"
                "We recommend scheduling a 30-minute scoping workshop to clarify technical specifications, data pipelines, "
                "and delivery milestones so we can prepare a tailored Proposal and Scope of Work (SOW)."
            )
        else: # Cold / Exploratory
            cta_block = (
                "To ensure we provide the most accurate guidance, we have attached our Project Scoping Questionnaire "
                "and standard Engagement Models Overview.\n\n"
                "Once you review these materials, please let us know when you would like to connect for an introductory consultation."
            )

        response_body = f"""Dear {client_display},

Thank you for reaching out to Cynbit Technologies{company_display}. We have received your inquiry regarding {customer_intent.lower()} in {service_category}.

{intro_paragraph}

{tech_mention}
{comm_sentence}

{cta_block}

You can conveniently book a time on our Solutions Engineering calendar or reply directly to this message. We look forward to the opportunity to partner with you.

Warm regards,

Solutions Engineering Team
Cynbit Technologies Inc.
hello@cynbit.com | https://cynbit.com
"""
        return response_body.strip()

    def _call_gemini_api(
        self,
        api_key: str,
        client_display: str,
        company_display: str,
        inquiry_text: str,
        service_category: str,
        budget_raw: str,
        timeline_raw: str,
        priority: str,
        detected_technologies: list
    ) -> Optional[str]:
        """Calls Gemini API safely via HTTP if key is available."""
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
        headers = {"Content-Type": "application/json"}
        prompt = f"""
You are a Senior Solutions Architect at Cynbit Technologies writing a personalized, executive-level business response to a prospective client.

Client Name: {client_display}
Client Company: {company_display}
Service Category: {service_category}
Target Budget: {budget_raw}
Target Timeline: {timeline_raw}
Lead Priority: {priority}
Detected Technologies: {', '.join(detected_technologies)}
Customer Inquiry:
"{inquiry_text}"

Write a concise, highly professional, warm business response that acknowledges their specific technical problem, highlights Cynbit's relevant expertise, respects their timeline/budget, and offers a clear call-to-action tailored to their priority level.
Do not include subject lines or placeholder tokens. Sign off as Solutions Engineering Team, Cynbit Technologies.
"""
        payload = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.4, "maxOutputTokens": 600}
        }
        try:
            resp = requests.post(url, json=payload, headers=headers, timeout=5)
            if resp.status_code == 200:
                data = resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"].strip()
        except Exception as e:
            print(f"LLM API request error: {e}")
        return None

# Global singleton
response_service = ResponseGeneratorService()
