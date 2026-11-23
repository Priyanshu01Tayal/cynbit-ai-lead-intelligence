"""
Cynbit AI - Analytics Endpoints
Provides real-time aggregated metrics, conversion funnel, category distributions,
and lead score intelligence.
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.lead import LeadModel

router = APIRouter(prefix="/api/analytics", tags=["Analytics"])

@router.get("/summary")
def get_analytics_summary(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Computes executive-level KPIs."""
    total = db.query(LeadModel).count()
    if total == 0:
        return {
            "total_leads": 0,
            "hot_leads": 0,
            "warm_leads": 0,
            "cold_leads": 0,
            "avg_score": 0.0,
            "conversion_rate": 0.0,
            "pipeline_value_estimated": 0.0,
            "status_counts": {},
            "category_counts": {},
            "priority_counts": {}
        }
        
    hot_count = db.query(LeadModel).filter(LeadModel.priority == "Hot").count()
    warm_count = db.query(LeadModel).filter(LeadModel.priority == "Warm").count()
    cold_count = db.query(LeadModel).filter(LeadModel.priority == "Cold").count()
    
    avg_score_res = db.query(func.avg(LeadModel.score)).scalar() or 0.0
    total_pipeline = db.query(func.sum(LeadModel.budget_estimated)).scalar() or 0.0
    
    # Conversion rate: Closed-Won / Total
    closed_won = db.query(LeadModel).filter(LeadModel.status == "Closed-Won").count()
    conversion_rate = round((closed_won / total) * 100, 2)
    
    # Groupings
    status_group = db.query(LeadModel.status, func.count(LeadModel.id)).group_by(LeadModel.status).all()
    status_counts = {s: c for s, c in status_group}
    
    cat_group = db.query(LeadModel.service_category, func.count(LeadModel.id)).group_by(LeadModel.service_category).all()
    category_counts = {cat: c for cat, c in cat_group}
    
    priority_counts = {"Hot": hot_count, "Warm": warm_count, "Cold": cold_count}
    
    return {
        "total_leads": total,
        "hot_leads": hot_count,
        "warm_leads": warm_count,
        "cold_leads": cold_count,
        "avg_score": round(float(avg_score_res), 1),
        "conversion_rate": conversion_rate,
        "pipeline_value_estimated": float(total_pipeline),
        "status_counts": status_counts,
        "category_counts": category_counts,
        "priority_counts": priority_counts
    }

@router.get("/funnel")
def get_conversion_funnel(db: Session = Depends(get_db)) -> List[Dict[str, Any]]:
    """Calculates the standard CRM conversion funnel stages."""
    stages = [
        ("Inquiries (New)", "New"),
        ("Contacted", "Contacted"),
        ("Qualified", "Qualified"),
        ("Proposal Sent", "Proposal Sent"),
        ("Negotiation", "Negotiation"),
        ("Closed-Won", "Closed-Won")
    ]
    
    # Cumulative pipeline stages
    stage_names = [s[1] for s in stages]
    stage_orders = {
        "New": 1,
        "Contacted": 2,
        "Qualified": 3,
        "Proposal Sent": 4,
        "Negotiation": 5,
        "Closed-Won": 6
    }
    
    total_leads = db.query(LeadModel).count()
    if total_leads == 0:
        return []
        
    funnel_data = []
    # For a funnel, any lead at stage >= order is considered to have passed earlier stages
    # Or count leads currently in each stage:
    counts_by_status = dict(db.query(LeadModel.status, func.count(LeadModel.id)).group_by(LeadModel.status).all())
    
    # Let's compute progressive funnel volume
    # Cumulative reaches
    cumulative = 0
    stage_counts = []
    for label, status_key in reversed(stages):
        count_at_stage = counts_by_status.get(status_key, 0)
        cumulative += count_at_stage
        stage_counts.append((label, cumulative, count_at_stage))
        
    stage_counts.reverse()
    top_volume = stage_counts[0][1] if stage_counts else 1
    
    for label, cum_count, exact_count in stage_counts:
        pct_of_total = round((cum_count / max(1, top_volume)) * 100, 1)
        funnel_data.append({
            "stage": label,
            "cumulative_count": cum_count,
            "current_stage_count": exact_count,
            "conversion_pct": pct_of_total
        })
        
    return funnel_data

@router.get("/distributions")
def get_distributions(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Provides detailed cross-tabulations for visualization."""
    leads = db.query(LeadModel).all()
    
    category_priority: Dict[str, Dict[str, int]] = {}
    urgency_priority: Dict[str, Dict[str, int]] = {}
    score_distribution = []
    budget_tiers = {"< $10k": 0, "$10k-$25k": 0, "$25k-$50k": 0, "> $50k": 0}
    
    for l in leads:
        # Category x Priority
        cat = l.service_category or "Other"
        prio = l.priority or "Warm"
        if cat not in category_priority:
            category_priority[cat] = {"Hot": 0, "Warm": 0, "Cold": 0}
        category_priority[cat][prio] = category_priority[cat].get(prio, 0) + 1
        
        # Urgency x Priority
        urg = l.urgency_level or "Medium"
        if urg not in urgency_priority:
            urgency_priority[urg] = {"Hot": 0, "Warm": 0, "Cold": 0}
        urgency_priority[urg][prio] = urgency_priority[urg].get(prio, 0) + 1
        
        # Score
        score_distribution.append(l.score)
        
        # Budget
        b = l.budget_estimated or 0.0
        if b >= 50000:
            budget_tiers["> $50k"] += 1
        elif b >= 25000:
            budget_tiers["$25k-$50k"] += 1
        elif b >= 10000:
            budget_tiers["$10k-$25k"] += 1
        else:
            budget_tiers["< $10k"] += 1
            
    return {
        "category_priority": category_priority,
        "urgency_priority": urgency_priority,
        "score_distribution": score_distribution,
        "budget_tiers": budget_tiers
    }
