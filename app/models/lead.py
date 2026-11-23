"""
Cynbit AI - Database ORM Model
Defines the persistent Lead record in SQLite.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Text, DateTime
from app.database import Base

class LeadModel(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    lead_id = Column(String(32), unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Client Metadata
    client_name = Column(String(128), default="Anonymous")
    client_email = Column(String(128), default="")
    client_company = Column(String(128), default="")
    
    # Raw Inquiry
    inquiry_text = Column(Text, nullable=False)
    
    # ML & Extraction Results
    service_category = Column(String(64), index=True, nullable=False)
    category_confidence = Column(Float, default=0.0)
    customer_intent = Column(String(128), default="General Inquiry")
    extracted_requirements = Column(Text, default="[]") # JSON-serialized list
    detected_technologies = Column(Text, default="[]")  # JSON-serialized list
    
    # Financial & Delivery Dimensions
    budget_estimated = Column(Float, default=0.0)
    budget_raw = Column(String(64), default="Unspecified")
    timeline_raw = Column(String(64), default="Flexible")
    urgency_level = Column(String(32), index=True, default="Medium")
    
    # Qualification & Scoring
    score = Column(Integer, index=True, default=50)
    priority = Column(String(16), index=True, default="Warm") # Hot, Warm, Cold
    score_reasons = Column(Text, default="[]")                # JSON-serialized list
    score_breakdown = Column(Text, default="{}")              # JSON-serialized dict
    action_recommendation = Column(Text, default="")
    
    # Generated Business Output
    suggested_response = Column(Text, default="")
    response_engine = Column(String(64), default="Template")
    
    # CRM Lifecycle
    # Statuses: New, Contacted, Qualified, Proposal Sent, Negotiation, Closed-Won, Closed-Lost
    status = Column(String(32), index=True, default="New")
    notes = Column(Text, default="")
