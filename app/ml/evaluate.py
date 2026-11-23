"""
Cynbit AI - Model Evaluation & Metrics Helpers
Provides functions to load and inspect evaluation results.
"""

import os
import json
from typing import Dict, Any, Optional

METRICS_PATH = "models/model_metrics.json"

def get_model_metrics(path: str = METRICS_PATH) -> Optional[Dict[str, Any]]:
    """Loads saved model metrics from disk."""
    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading model metrics: {e}")
            return None
    return None

def is_model_trained(path: str = "models/lead_classifier.joblib") -> bool:
    """Checks whether the trained model exists."""
    return os.path.exists(path)
