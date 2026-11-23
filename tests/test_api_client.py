"""
Cynbit AI - Unit Tests for Frontend API Client
Tests initialization, environment variable resolution, error handling, and endpoint requests.
"""

import os
import pytest
from unittest.mock import patch, MagicMock
import requests

from frontend.utils.api_client import CynbitAPIClient, APIClientError, DEFAULT_API_BASE_URL

def test_api_client_initialization_defaults():
    with patch.dict(os.environ, {}, clear=True):
        client = CynbitAPIClient()
        assert client.base_url == DEFAULT_API_BASE_URL
        assert client.timeout == 20

def test_api_client_initialization_custom_env():
    custom_url = "https://custom-api.cynbit.internal"
    with patch.dict(os.environ, {"API_BASE_URL": custom_url}):
        client = CynbitAPIClient()
        assert client.base_url == custom_url

def test_api_client_initialization_strip_trailing_slash():
    client = CynbitAPIClient(base_url="https://api.cynbit.com/")
    assert client.base_url == "https://api.cynbit.com"

@patch("requests.Session.request")
def test_get_health_success(mock_request):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.json.return_value = {"status": "healthy", "model_loaded": True, "lead_count": 48}
    mock_request.return_value = mock_resp

    client = CynbitAPIClient(base_url="http://testserver")
    health = client.get_health()

    assert health["status"] == "healthy"
    assert health["model_loaded"] is True
    mock_request.assert_called_once_with(method="GET", url="http://testserver/api/health", timeout=12)

@patch("requests.Session.request")
def test_analyze_inquiry_payload(mock_request):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.json.return_value = {"score": 88, "priority": "Hot", "service_category": "AI/ML Development"}
    mock_request.return_value = mock_resp

    client = CynbitAPIClient(base_url="http://testserver")
    res = client.analyze_inquiry(
        inquiry_text="Build custom defect detection computer vision",
        client_name="Test Client",
        client_company="Acme Corp"
    )

    assert res["score"] == 88
    assert res["priority"] == "Hot"
    mock_request.assert_called_once()
    call_kwargs = mock_request.call_args[1]
    assert call_kwargs["json"]["inquiry_text"] == "Build custom defect detection computer vision"
    assert call_kwargs["json"]["client_name"] == "Test Client"

@patch("requests.Session.request")
def test_list_leads_query_params(mock_request):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.json.return_value = [{"lead_id": "CYN-2026-001"}]
    mock_request.return_value = mock_resp

    client = CynbitAPIClient(base_url="http://testserver")
    leads = client.list_leads(
        search="Vision",
        category="AI/ML Development",
        priority="Hot",
        status="New",
        min_score=70,
        limit=10
    )

    assert len(leads) == 1
    call_params = mock_request.call_args[1]["params"]
    assert call_params["search"] == "Vision"
    assert call_params["category"] == "AI/ML Development"
    assert call_params["priority"] == "Hot"
    assert call_params["status"] == "New"
    assert call_params["min_score"] == 70
    assert call_params["limit"] == 10

@patch("requests.Session.request")
def test_timeout_error_handling(mock_request):
    mock_request.side_effect = requests.exceptions.Timeout("Read timed out")

    client = CynbitAPIClient(base_url="http://testserver")
    with pytest.raises(APIClientError) as exc_info:
        client.get_health()

    assert exc_info.value.status_code == 408
    assert "timed out" in str(exc_info.value)

@patch("requests.Session.request")
def test_connection_error_handling(mock_request):
    mock_request.side_effect = requests.exceptions.ConnectionError("Connection refused")

    client = CynbitAPIClient(base_url="http://testserver")
    with pytest.raises(APIClientError) as exc_info:
        client.get_health()

    assert exc_info.value.status_code == 503
    assert "Could not connect to backend server" in str(exc_info.value)

@patch("requests.Session.request")
def test_http_error_handling_with_detail(mock_request):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
    mock_resp.status_code = 404
    mock_resp.headers = {"Content-Type": "application/json"}
    mock_resp.json.return_value = {"detail": "Lead not found"}
    mock_request.return_value = mock_resp

    client = CynbitAPIClient(base_url="http://testserver")
    with pytest.raises(APIClientError) as exc_info:
        client.get_lead("INVALID-999")

    assert exc_info.value.status_code == 404
    assert "Lead not found" in str(exc_info.value)
