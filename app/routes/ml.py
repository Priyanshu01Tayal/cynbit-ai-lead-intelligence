"""
Cynbit AI - ML Management Endpoints
Provides model evaluation metrics, top features, confusion matrix data,
and on-demand model retraining.
"""

from fastapi import APIRouter, HTTPException
from app.ml.evaluate import get_model_metrics, is_model_trained
from app.ml.train import train_lead_classifier
from app.services.lead_service import lead_service

router = APIRouter(prefix="/api/ml", tags=["Machine Learning"])

@router.get("/metrics")
def get_metrics():
    """Returns the saved test-set evaluation metrics for the active ML model."""
    metrics = get_model_metrics()
    if not metrics:
        if not is_model_trained():
            # Trigger initial training automatically
            try:
                metrics = train_lead_classifier()
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Failed to train baseline model: {str(e)}")
        else:
            raise HTTPException(status_code=404, detail="Model metrics file not found.")
            
    return metrics

@router.post("/retrain")
def retrain_model():
    """Retrains the TF-IDF + Logistic Regression model and reloads the pipeline."""
    try:
        metrics = train_lead_classifier()
        # Reload pipeline in memory
        lead_service.reload_model()
        return {
            "status": "success",
            "message": "Model retrained and reloaded into active memory successfully.",
            "metrics": metrics
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model retraining failed: {str(e)}")
