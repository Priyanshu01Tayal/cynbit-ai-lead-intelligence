"""
Cynbit AI - Pydantic Request & Response Schemas
Provides strict validation and API contracts.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict

class LeadAnalyzeRequest(BaseModel):
    inquiry_text: str = Field(..., min_length=5, description="Raw customer inquiry text")
    client_name: Optional[str] = Field("", description="Client full name")
    client_email: Optional[str] = Field("", description="Client email address")
    client_company: Optional[str] = Field("", description="Client company or organization")
    manual_category: Optional[str] = Field(None, description="Optional manual override for service category")

class LeadCreateRequest(BaseModel):
    inquiry_text: str = Field(..., min_length=5)
    client_name: Optional[str] = ""
    client_email: Optional[str] = ""
    client_company: Optional[str] = ""
    manual_category: Optional[str] = None
    notes: Optional[str] = ""

class LeadUpdateRequest(BaseModel):
    status: Optional[str] = Field(None, description="New CRM status: New, Contacted, Qualified, Proposal Sent, Negotiation, Closed-Won, Closed-Lost")
    notes: Optional[str] = None
    client_name: Optional[str] = None
    client_email: Optional[str] = None
    client_company: Optional[str] = None
    service_category: Optional[str] = None
    priority: Optional[str] = None
    score: Optional[int] = None

class LeadResponse(BaseModel):
    id: int
    lead_id: str
    created_at: datetime
    updated_at: Optional[datetime] = None
    client_name: str
    client_email: str
    client_company: str
    inquiry_text: str
    service_category: str
    category_confidence: float
    customer_intent: str
    extracted_requirements: List[str]
    detected_technologies: List[str]
    budget_estimated: float
    budget_raw: str
    timeline_raw: str
    urgency_level: str
    score: int
    priority: str
    score_reasons: List[str]
    score_breakdown: Dict[str, Any]
    action_recommendation: str
    suggested_response: str
    response_engine: str
    status: str
    notes: str

    model_config = ConfigDict(from_attributes=True)

class LeadAnalysisResult(BaseModel):
    client_name: str
    client_email: str
    client_company: str
    inquiry_text: str
    service_category: str
    category_confidence: float
    classification_details: Dict[str, Any]
    customer_intent: str
    detected_technologies: List[str]
    extracted_requirements: List[str]
    budget_estimated: Optional[float]
    budget_raw: str
    timeline_raw: str
    urgency_level: str
    score: int
    priority: str
    score_breakdown: Dict[str, Any]
    score_reasons: List[str]
    action_recommendation: str
    suggested_response: str
    response_engine: str

class AnalyticsSummaryResponse(BaseModel):
    total_leads: int
    hot_leads: int
    warm_leads: int
    cold_leads: int
    avg_score: float
    conversion_rate: float
    pipeline_value_estimated: float
    status_counts: Dict[str, int]
    category_counts: Dict[str, int]
    priority_counts: Dict[str, int]

class ModelRetrainResponse(BaseModel):
    status: str
    message: str
    metrics: Dict[str, Any]
