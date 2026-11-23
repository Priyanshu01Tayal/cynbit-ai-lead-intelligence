"""
Cynbit AI - Lead API Endpoints
Handles lead creation, real-time AI analysis, management, updates, and CSV export.
"""

import io
import csv
import json
import random
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from sqlalchemy import or_, desc, asc

from app.database import get_db
from app.models.lead import LeadModel
from app.schemas.lead import (
    LeadAnalyzeRequest,
    LeadAnalysisResult,
    LeadCreateRequest,
    LeadUpdateRequest,
    LeadResponse
)
from app.services.lead_service import lead_service

router = APIRouter(prefix="/api/leads", tags=["Leads"])

def _model_to_dict(lead: LeadModel) -> dict:
    """Helper to convert LeadModel into Pydantic-compatible dictionary with parsed JSON fields."""
    return {
        "id": lead.id,
        "lead_id": lead.lead_id,
        "created_at": lead.created_at,
        "updated_at": lead.updated_at,
        "client_name": lead.client_name or "",
        "client_email": lead.client_email or "",
        "client_company": lead.client_company or "",
        "inquiry_text": lead.inquiry_text,
        "service_category": lead.service_category,
        "category_confidence": lead.category_confidence,
        "customer_intent": lead.customer_intent or "",
        "extracted_requirements": json.loads(lead.extracted_requirements) if lead.extracted_requirements else [],
        "detected_technologies": json.loads(lead.detected_technologies) if lead.detected_technologies else [],
        "budget_estimated": lead.budget_estimated or 0.0,
        "budget_raw": lead.budget_raw or "Unspecified",
        "timeline_raw": lead.timeline_raw or "Flexible",
        "urgency_level": lead.urgency_level or "Medium",
        "score": lead.score or 0,
        "priority": lead.priority or "Warm",
        "score_reasons": json.loads(lead.score_reasons) if lead.score_reasons else [],
        "score_breakdown": json.loads(lead.score_breakdown) if lead.score_breakdown else {},
        "action_recommendation": lead.action_recommendation or "",
        "suggested_response": lead.suggested_response or "",
        "response_engine": lead.response_engine or "Template",
        "status": lead.status or "New",
        "notes": lead.notes or ""
    }

@router.post("/analyze", response_model=LeadAnalysisResult)
def analyze_inquiry(request: LeadAnalyzeRequest):
    """
    Analyzes an unstructured customer inquiry text in real-time.
    Runs ML classification, entity extraction, multidimensional scoring, and response generation.
    Does not persist to database (ideal for instant preview).
    """
    try:
        result = lead_service.analyze_lead_inquiry(
            inquiry_text=request.inquiry_text,
            client_name=request.client_name or "",
            client_email=request.client_email or "",
            client_company=request.client_company or "",
            manual_category=request.manual_category
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lead analysis failed: {str(e)}")

@router.post("", response_model=LeadResponse, status_code=201)
def create_lead(request: LeadCreateRequest, db: Session = Depends(get_db)):
    """
    Analyzes and saves a new lead persistently into SQLite.
    """
    try:
        analysis = lead_service.analyze_lead_inquiry(
            inquiry_text=request.inquiry_text,
            client_name=request.client_name or "Anonymous",
            client_email=request.client_email or "",
            client_company=request.client_company or "",
            manual_category=request.manual_category
        )
        
        # Generate Unique Lead ID
        count = db.query(LeadModel).count()
        lead_id = f"CYN-2026-{count + 1:03d}"
        
        db_lead = LeadModel(
            lead_id=lead_id,
            client_name=analysis["client_name"],
            client_email=analysis["client_email"],
            client_company=analysis["client_company"],
            inquiry_text=analysis["inquiry_text"],
            service_category=analysis["service_category"],
            category_confidence=analysis["category_confidence"],
            customer_intent=analysis["customer_intent"],
            extracted_requirements=json.dumps(analysis["extracted_requirements"]),
            detected_technologies=json.dumps(analysis["detected_technologies"]),
            budget_estimated=analysis["budget_estimated"] or 0.0,
            budget_raw=analysis["budget_raw"],
            timeline_raw=analysis["timeline_raw"],
            urgency_level=analysis["urgency_level"],
            score=analysis["score"],
            priority=analysis["priority"],
            score_reasons=json.dumps(analysis["score_reasons"]),
            score_breakdown=json.dumps(analysis["score_breakdown"]),
            action_recommendation=analysis["action_recommendation"],
            suggested_response=analysis["suggested_response"],
            response_engine=analysis["response_engine"],
            status="New",
            notes=request.notes or ""
        )
        
        db.add(db_lead)
        db.commit()
        db.refresh(db_lead)
        
        return _model_to_dict(db_lead)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Failed to create lead: {str(e)}")

@router.get("", response_model=List[LeadResponse])
def list_leads(
    search: Optional[str] = None,
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    min_score: Optional[int] = None,
    max_score: Optional[int] = None,
    sort_by: str = "created_at",
    order: str = "desc",
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """Lists leads with dynamic search, multi-field filtering, sorting, and pagination."""
    query = db.query(LeadModel)
    
    if search and isinstance(search, str) and search.strip():
        term = f"%{search.strip()}%"
        query = query.filter(
            or_(
                LeadModel.client_name.ilike(term),
                LeadModel.client_company.ilike(term),
                LeadModel.inquiry_text.ilike(term),
                LeadModel.lead_id.ilike(term)
            )
        )
        
    if category and category != "All":
        query = query.filter(LeadModel.service_category == category)
        
    if priority and priority != "All":
        query = query.filter(LeadModel.priority == priority)
        
    if status and status != "All":
        query = query.filter(LeadModel.status == status)
        
    if min_score is not None:
        query = query.filter(LeadModel.score >= min_score)
        
    if max_score is not None:
        query = query.filter(LeadModel.score <= max_score)
        
    # Sorting
    sort_col = getattr(LeadModel, sort_by, LeadModel.created_at)
    query = query.order_by(desc(sort_col) if order == "desc" else asc(sort_col))
    
    leads = query.offset(skip).limit(limit).all()
    return [_model_to_dict(l) for l in leads]

@router.get("/{lead_identifier}", response_model=LeadResponse)
def get_lead(lead_identifier: str, db: Session = Depends(get_db)):
    """Retrieves single lead by integer ID or string lead_id (e.g. CYN-2026-001)."""
    lead = None
    if lead_identifier.isdigit():
        lead = db.query(LeadModel).filter(LeadModel.id == int(lead_identifier)).first()
    if not lead:
        lead = db.query(LeadModel).filter(LeadModel.lead_id == lead_identifier).first()
        
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    return _model_to_dict(lead)

@router.put("/{lead_identifier}", response_model=LeadResponse)
def update_lead(lead_identifier: str, updates: LeadUpdateRequest, db: Session = Depends(get_db)):
    """Updates lead CRM status, notes, or contact info."""
    lead = None
    if lead_identifier.isdigit():
        lead = db.query(LeadModel).filter(LeadModel.id == int(lead_identifier)).first()
    if not lead:
        lead = db.query(LeadModel).filter(LeadModel.lead_id == lead_identifier).first()
        
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    if updates.status is not None:
        lead.status = updates.status
    if updates.notes is not None:
        lead.notes = updates.notes
    if updates.client_name is not None:
        lead.client_name = updates.client_name
    if updates.client_email is not None:
        lead.client_email = updates.client_email
    if updates.client_company is not None:
        lead.client_company = updates.client_company
    if updates.priority is not None:
        lead.priority = updates.priority
    if updates.score is not None:
        lead.score = updates.score
    if updates.service_category is not None:
        lead.service_category = updates.service_category
        
    lead.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(lead)
    return _model_to_dict(lead)

@router.delete("/{lead_identifier}")
def delete_lead(lead_identifier: str, db: Session = Depends(get_db)):
    """Deletes a lead from the database."""
    lead = None
    if lead_identifier.isdigit():
        lead = db.query(LeadModel).filter(LeadModel.id == int(lead_identifier)).first()
    if not lead:
        lead = db.query(LeadModel).filter(LeadModel.lead_id == lead_identifier).first()
        
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
        
    db.delete(lead)
    db.commit()
    return {"status": "success", "message": f"Lead {lead.lead_id} deleted successfully"}

@router.get("/export/csv")
def export_leads_csv(
    category: Optional[str] = None,
    priority: Optional[str] = None,
    status: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Exports leads as downloadable CSV file."""
    query = db.query(LeadModel)
    if category and category != "All":
        query = query.filter(LeadModel.service_category == category)
    if priority and priority != "All":
        query = query.filter(LeadModel.priority == priority)
    if status and status != "All":
        query = query.filter(LeadModel.status == status)
        
    leads = query.order_by(desc(LeadModel.created_at)).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    
    # Write Header
    writer.writerow([
        "Lead ID", "Date Created", "Client Name", "Email", "Company",
        "Service Category", "Category Confidence", "Score", "Priority",
        "CRM Status", "Estimated Budget", "Budget Raw", "Timeline",
        "Urgency", "Customer Intent", "Inquiry Text", "Notes"
    ])
    
    for l in leads:
        writer.writerow([
            l.lead_id,
            l.created_at.strftime("%Y-%m-%d %H:%M:%S") if l.created_at else "",
            l.client_name,
            l.client_email,
            l.client_company,
            l.service_category,
            f"{l.category_confidence:.2f}",
            l.score,
            l.priority,
            l.status,
            f"${l.budget_estimated:,.0f}" if l.budget_estimated else "$0",
            l.budget_raw,
            l.timeline_raw,
            l.urgency_level,
            l.customer_intent,
            l.inquiry_text.replace("\n", " "),
            l.notes.replace("\n", " ") if l.notes else ""
        ])
        
    output.seek(0)
    filename = f"cynbit_leads_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )

@router.post("/seed", status_code=200)
def seed_historical_leads(force: bool = False, db: Session = Depends(get_db)):
    """Seeds sample historical leads into SQLite if table is empty or if force=True."""
    current_count = db.query(LeadModel).count()
    if current_count > 0 and not force:
        return {"status": "skipped", "message": f"Database already contains {current_count} leads."}
        
    import os
    import pandas as pd
    sample_csv_path = os.path.join("data", "sample_leads.csv")
    if not os.path.exists(sample_csv_path):
        from data.generate_datasets import generate_sample_leads
        generate_sample_leads()
        
    df = pd.read_csv(sample_csv_path)
    inserted = 0
    for _, row in df.iterrows():
        lead_id = str(row["lead_id"])
        # Skip if already exists
        if db.query(LeadModel).filter(LeadModel.lead_id == lead_id).first():
            continue
            
        created_dt = datetime.strptime(str(row["created_at"]), "%Y-%m-%d %H:%M:%S") if "created_at" in row and pd.notna(row["created_at"]) else datetime.utcnow()
        
        # Deterministic instant seed
        reqs = [f"Domain-tailored technical specifications for {row['service_category']}"]
        techs = []
        if "AWS" in str(row["inquiry_text"]): techs.append("AWS")
        if "React" in str(row["inquiry_text"]): techs.append("React")
        if "Flutter" in str(row["inquiry_text"]): techs.append("Flutter")
        if "Kubernetes" in str(row["inquiry_text"]): techs.append("Kubernetes")
        if "AI" in str(row["inquiry_text"]): techs.append("PyTorch")
        
        reasons = [
            f"Budget alignment: {row.get('budget_raw', 'Standard commercial budget')}",
            f"Project urgency factor: {row.get('urgency_level', 'Medium')} priority timeframe",
            f"Service relevance: High strategic fit in {row['service_category']}"
        ]
        
        db_lead = LeadModel(
            lead_id=lead_id,
            created_at=created_dt,
            client_name=str(row["client_name"]),
            client_email=str(row["client_email"]),
            client_company=str(row["client_company"]),
            inquiry_text=str(row["inquiry_text"]),
            service_category=str(row["service_category"]),
            category_confidence=float(row.get("category_confidence", 0.92)),
            customer_intent=str(row.get("customer_intent", "New Product Development")),
            extracted_requirements=json.dumps(reqs),
            detected_technologies=json.dumps(techs),
            budget_estimated=float(row["budget_estimated"]) if pd.notna(row["budget_estimated"]) else 0.0,
            budget_raw=str(row.get("budget_raw", "Unspecified")),
            timeline_raw=str(row.get("timeline_raw", "2 months")),
            urgency_level=str(row.get("urgency_level", "Medium")),
            score=int(row.get("score", 70)),
            priority=str(row.get("priority", "Warm")),
            score_reasons=json.dumps(reasons),
            score_breakdown=json.dumps({
                "budget": {"score": 22, "max": 30},
                "urgency": {"score": 18, "max": 25},
                "requirements": {"score": 15, "max": 20},
                "timeline": {"score": 12, "max": 15},
                "relevance": {"score": 8, "max": 10}
            }),
            action_recommendation=f"Follow up within 24h regarding {row['service_category']}.",
            suggested_response=f"Dear {row['client_name']},\n\nThank you for reaching out to Cynbit Technologies regarding your {row['service_category']} initiative.\n\nWarm regards,\nCynbit Solutions Team",
            response_engine="Cynbit Expert Rule & Template Engine",
            status=str(row.get("status", "New")),
            notes=str(row.get("notes", "Historical lead"))
        )
        db.add(db_lead)
        inserted += 1
        
    db.commit()
    return {"status": "success", "message": f"Seeded {inserted} historical leads into database."}
