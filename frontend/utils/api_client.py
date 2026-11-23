"""
Cynbit AI - Centralized Frontend API Client
Manages all HTTP communication between the Streamlit frontend and the FastAPI backend.
"""

import os
import requests
from typing import Dict, Any, List, Optional, Union

# Default fallback to deployed Render backend
DEFAULT_API_BASE_URL = "https://cynbit-ai-lead-intelligence.onrender.com"

class APIClientError(Exception):
    """Custom exception raised when backend API call fails."""
    def __init__(self, message: str, status_code: Optional[int] = None, details: Optional[Any] = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.details = details

    def __str__(self):
        if self.status_code:
            return f"[{self.status_code}] {self.message}"
        return self.message


class CynbitAPIClient:
    """
    Centralized HTTP client for Cynbit Lead Intelligence Platform.
    Handles communication, error reporting, timeouts, and JSON serialization.
    """
    def __init__(self, base_url: Optional[str] = None, timeout: int = 20):
        # Read from environment variable or parameter, falling back to Render production
        env_url = os.getenv("API_BASE_URL", "").strip()
        self.base_url = (base_url or env_url or DEFAULT_API_BASE_URL).rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "CynbitAI-StreamlitFrontend/1.0"
        })

    def _url(self, path: str) -> str:
        """Constructs full URL from path."""
        if not path.startswith("/"):
            path = f"/{path}"
        return f"{self.base_url}{path}"

    def _handle_response(self, response: requests.Response) -> Any:
        """Checks HTTP status codes and extracts JSON or raises APIClientError."""
        try:
            response.raise_for_status()
            if response.headers.get("Content-Type", "").startswith("application/json"):
                return response.json()
            return response.text
        except requests.exceptions.HTTPError as e:
            error_detail = response.text
            try:
                json_err = response.json()
                if "detail" in json_err:
                    error_detail = json_err["detail"]
            except Exception:
                pass
            raise APIClientError(
                message=f"API request failed: {error_detail}",
                status_code=response.status_code,
                details=error_detail
            ) from e

    def _safe_request(self, method: str, path: str, timeout: Optional[int] = None, **kwargs) -> Any:
        """Executes a request with unified error handling for timeouts and connectivity."""
        url = self._url(path)
        eff_timeout = timeout or self.timeout
        try:
            resp = self.session.request(method=method, url=url, timeout=eff_timeout, **kwargs)
            return self._handle_response(resp)
        except requests.exceptions.Timeout as e:
            raise APIClientError(
                message=f"Connection timed out ({eff_timeout}s) while calling backend at {self.base_url}. "
                        "If the backend is hosted on a free cloud instance (e.g. Render), it may take 30–50 seconds to wake up from idle sleep. "
                        "Please refresh in a few moments.",
                status_code=408
            ) from e
        except requests.exceptions.ConnectionError as e:
            raise APIClientError(
                message=f"Could not connect to backend server at {self.base_url}. "
                        "Please check network connectivity or verify that the API service is online.",
                status_code=503
            ) from e
        except APIClientError:
            raise
        except Exception as e:
            raise APIClientError(message=f"Unexpected error: {str(e)}") from e

    # ==================== Health & Telemetry ====================

    def get_health(self) -> Dict[str, Any]:
        """Checks API health and service metadata."""
        return self._safe_request("GET", "/api/health", timeout=12)

    # ==================== Lead Intelligence & Analysis ====================

    def analyze_inquiry(
        self,
        inquiry_text: str,
        client_name: str = "",
        client_email: str = "",
        client_company: str = "",
        manual_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Runs real-time ML classification, entity extraction, scoring, and proposal drafting.
        Does not persist to database.
        """
        payload = {
            "inquiry_text": inquiry_text,
            "client_name": client_name,
            "client_email": client_email,
            "client_company": client_company,
            "manual_category": manual_category
        }
        return self._safe_request("POST", "/api/leads/analyze", json=payload, timeout=25)

    def create_lead(
        self,
        inquiry_text: str,
        client_name: str = "Anonymous",
        client_email: str = "",
        client_company: str = "",
        manual_category: Optional[str] = None,
        notes: str = ""
    ) -> Dict[str, Any]:
        """Analyzes and persists a new lead into the backend database."""
        payload = {
            "inquiry_text": inquiry_text,
            "client_name": client_name,
            "client_email": client_email,
            "client_company": client_company,
            "manual_category": manual_category,
            "notes": notes
        }
        return self._safe_request("POST", "/api/leads", json=payload, timeout=25)

    def list_leads(
        self,
        search: Optional[str] = None,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None,
        min_score: Optional[int] = None,
        max_score: Optional[int] = None,
        sort_by: str = "created_at",
        order: str = "desc",
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieves leads with filtering, search, sorting, and pagination."""
        params: Dict[str, Any] = {
            "sort_by": sort_by,
            "order": order,
            "skip": skip,
            "limit": limit
        }
        if search and search.strip():
            params["search"] = search.strip()
        if category and category != "All":
            params["category"] = category
        if priority and priority != "All":
            params["priority"] = priority
        if status and status != "All":
            params["status"] = status
        if min_score is not None:
            params["min_score"] = min_score
        if max_score is not None:
            params["max_score"] = max_score

        return self._safe_request("GET", "/api/leads", params=params, timeout=20)

    def get_lead(self, lead_identifier: Union[int, str]) -> Dict[str, Any]:
        """Retrieves single lead by ID or string code (e.g. CYN-2026-001)."""
        return self._safe_request("GET", f"/api/leads/{lead_identifier}", timeout=15)

    def update_lead(
        self,
        lead_identifier: Union[int, str],
        status: Optional[str] = None,
        notes: Optional[str] = None,
        client_name: Optional[str] = None,
        client_email: Optional[str] = None,
        client_company: Optional[str] = None,
        priority: Optional[str] = None,
        score: Optional[int] = None,
        service_category: Optional[str] = None
    ) -> Dict[str, Any]:
        """Updates lead status, notes, contact data, or qualifications."""
        payload: Dict[str, Any] = {}
        if status is not None:
            payload["status"] = status
        if notes is not None:
            payload["notes"] = notes
        if client_name is not None:
            payload["client_name"] = client_name
        if client_email is not None:
            payload["client_email"] = client_email
        if client_company is not None:
            payload["client_company"] = client_company
        if priority is not None:
            payload["priority"] = priority
        if score is not None:
            payload["score"] = score
        if service_category is not None:
            payload["service_category"] = service_category

        return self._safe_request("PUT", f"/api/leads/{lead_identifier}", json=payload, timeout=20)

    def delete_lead(self, lead_identifier: Union[int, str]) -> Dict[str, Any]:
        """Deletes a lead from the backend database."""
        return self._safe_request("DELETE", f"/api/leads/{lead_identifier}", timeout=15)

    def export_csv(
        self,
        category: Optional[str] = None,
        priority: Optional[str] = None,
        status: Optional[str] = None
    ) -> bytes:
        """Downloads filtered leads formatted as a CSV stream."""
        params: Dict[str, Any] = {}
        if category and category != "All":
            params["category"] = category
        if priority and priority != "All":
            params["priority"] = priority
        if status and status != "All":
            params["status"] = status

        url = self._url("/api/leads/export/csv")
        try:
            resp = self.session.get(url, params=params, timeout=25)
            resp.raise_for_status()
            return resp.content
        except Exception as e:
            raise APIClientError(f"Failed to export CSV: {str(e)}") from e

    def seed_leads(self, force: bool = False) -> Dict[str, Any]:
        """Triggers historical lead database seeding."""
        return self._safe_request("POST", "/api/leads/seed", params={"force": force}, timeout=30)

    # ==================== Analytics Endpoints ====================

    def get_analytics_summary(self) -> Dict[str, Any]:
        """Fetches high-level executive KPI metrics."""
        return self._safe_request("GET", "/api/analytics/summary", timeout=15)

    def get_conversion_funnel(self) -> List[Dict[str, Any]]:
        """Fetches pipeline funnel progression."""
        return self._safe_request("GET", "/api/analytics/funnel", timeout=15)

    def get_distributions(self) -> Dict[str, Any]:
        """Fetches distribution cross-tabulations."""
        return self._safe_request("GET", "/api/analytics/distributions", timeout=15)

    # ==================== Machine Learning Endpoints ====================

    def get_metrics(self) -> Dict[str, Any]:
        """Fetches model test metrics, confusion matrix, and feature importances."""
        return self._safe_request("GET", "/api/ml/metrics", timeout=15)

    def retrain_model(self) -> Dict[str, Any]:
        """Triggers ML model retraining and pipeline reload (takes up to 45s)."""
        return self._safe_request("POST", "/api/ml/retrain", timeout=60)


# Global singleton instance for easy import across pages
api_client = CynbitAPIClient()
