"""
Live API and Database Verification Script
Starts a live Uvicorn server in a separate thread, executes comprehensive HTTP requests
against all endpoints, tests error conditions, verifies persistence, and shuts down cleanly.
"""

import threading
import time
import uvicorn
import requests
from app.main import app
from app.config import settings

class ServerThread(threading.Thread):
    def __init__(self, host="127.0.0.1", port=8001):
        super().__init__()
        self.host = host
        self.port = port
        self.config = uvicorn.Config(app=app, host=self.host, port=self.port, log_level="warning")
        self.server = uvicorn.Server(self.config)
        self.daemon = True

    def run(self):
        self.server.run()

    def stop(self):
        self.server.should_exit = True

def run_live_api_tests():
    port = 8001
    base_url = f"http://127.0.0.1:{port}"
    
    print("=" * 60)
    print("STARTING LIVE FASTAPI SERVER THREAD ON PORT 8001...")
    print("=" * 60)
    server_thread = ServerThread(port=port)
    server_thread.start()
    
    # Wait for server to bind
    time.sleep(2.0)
    
    results = {}
    try:
        # 1. Test Swagger Docs
        r_docs = requests.get(f"{base_url}/docs", timeout=5)
        print(f"1. GET /docs: Status {r_docs.status_code} ({'PASS' if r_docs.status_code == 200 else 'FAIL'})")
        results["docs"] = (r_docs.status_code == 200)

        # 2. Test /api/health
        r_health = requests.get(f"{base_url}/api/health", timeout=5)
        h_data = r_health.json()
        print(f"2. GET /api/health: Status {r_health.status_code}, DB: {h_data.get('database')}, Leads: {h_data.get('lead_count')}")
        results["health"] = (r_health.status_code == 200 and h_data.get("status") == "healthy")

        # 3. Test POST /api/leads/analyze
        analyze_payload = {
            "inquiry_text": "We need an AI/ML engineer to build a predictive customer churn model with PostgreSQL integration. Budget is $30,000 and deadline is 2 months.",
            "client_name": "Dr. Sarah Adams",
            "client_company": "BioGenius Labs"
        }
        r_analyze = requests.post(f"{base_url}/api/leads/analyze", json=analyze_payload, timeout=5)
        print(f"3. POST /api/leads/analyze: Status {r_analyze.status_code}, Category: {r_analyze.json().get('service_category')}, Score: {r_analyze.json().get('score')}")
        results["analyze"] = (r_analyze.status_code == 200 and r_analyze.json().get("service_category") == "AI/ML Development")

        # 4. Test POST /api/leads (Create)
        create_payload = {
            "inquiry_text": "Need a cloud DevOps specialist to containerize 12 services and setup AWS EKS with Terraform. Budget is $35,000, 2 months.",
            "client_name": "Marcus Vance",
            "client_email": "marcus@apexlogistics.com",
            "client_company": "Apex Logistics Global",
            "notes": "Direct live API audit test lead"
        }
        r_create = requests.post(f"{base_url}/api/leads", json=create_payload, timeout=5)
        created_lead = r_create.json()
        created_id = created_lead.get("lead_id")
        print(f"4. POST /api/leads: Status {r_create.status_code}, Created Lead ID: {created_id}")
        results["create_lead"] = (r_create.status_code == 201 and created_id is not None)

        # 5. Test GET /api/leads/{id}
        r_get = requests.get(f"{base_url}/api/leads/{created_id}", timeout=5)
        print(f"5. GET /api/leads/{created_id}: Status {r_get.status_code}, Client: {r_get.json().get('client_name')}")
        results["get_lead"] = (r_get.status_code == 200 and r_get.json().get("client_name") == "Marcus Vance")

        # 6. Test PUT /api/leads/{id}
        update_payload = {"status": "Proposal Sent", "notes": "Audited via live API test"}
        r_update = requests.put(f"{base_url}/api/leads/{created_id}", json=update_payload, timeout=5)
        print(f"6. PUT /api/leads/{created_id}: Status {r_update.status_code}, New Status: {r_update.json().get('status')}")
        results["update_lead"] = (r_update.status_code == 200 and r_update.json().get("status") == "Proposal Sent")

        # 7. Test GET /api/leads with filters
        r_list = requests.get(f"{base_url}/api/leads?category=Cloud %26 DevOps&limit=10", timeout=5)
        list_data = r_list.json()
        print(f"7. GET /api/leads?category=...: Status {r_list.status_code}, Found {len(list_data)} leads")
        results["list_leads"] = (r_list.status_code == 200 and len(list_data) >= 1)

        # 8. Test GET /api/leads/export/csv
        r_csv = requests.get(f"{base_url}/api/leads/export/csv", timeout=5)
        csv_len = len(r_csv.text)
        print(f"8. GET /api/leads/export/csv: Status {r_csv.status_code}, Content-Type: {r_csv.headers.get('content-type')}, CSV Bytes: {csv_len}")
        results["export_csv"] = (r_csv.status_code == 200 and "Lead ID" in r_csv.text)

        # 9. Test Analytics Endpoints
        r_summary = requests.get(f"{base_url}/api/analytics/summary", timeout=5)
        r_funnel = requests.get(f"{base_url}/api/analytics/funnel", timeout=5)
        print(f"9. GET /api/analytics/summary: Status {r_summary.status_code}, Total: {r_summary.json().get('total_leads')}")
        print(f"   GET /api/analytics/funnel: Status {r_funnel.status_code}, Stages: {len(r_funnel.json())}")
        results["analytics"] = (r_summary.status_code == 200 and r_funnel.status_code == 200)

        # 10. Test ML Metrics Endpoint
        r_ml = requests.get(f"{base_url}/api/ml/metrics", timeout=5)
        ml_data = r_ml.json()
        print(f"10. GET /api/ml/metrics: Status {r_ml.status_code}, Accuracy: {ml_data.get('overall', {}).get('accuracy')}")
        results["ml_metrics"] = (r_ml.status_code == 200 and "accuracy" in ml_data.get("overall", {}))

        # 11. Error Handling Tests
        r_404 = requests.get(f"{base_url}/api/leads/NONEXISTENT_9999", timeout=5)
        print(f"11. Error Handling 404 Check: Status {r_404.status_code} ({'PASS' if r_404.status_code == 404 else 'FAIL'})")
        results["404_handling"] = (r_404.status_code == 404)

        r_422 = requests.post(f"{base_url}/api/leads", json={"inquiry_text": "hi"}, timeout=5) # min_length=5 violation
        print(f"12. Error Handling 422 Check (Pydantic validation): Status {r_422.status_code} ({'PASS' if r_422.status_code == 422 else 'FAIL'})")
        results["422_handling"] = (r_422.status_code == 422)

    finally:
        print("\nShutting down live test server...")
        server_thread.stop()
        time.sleep(1.0)
        
    print("\n" + "=" * 60)
    print("LIVE API VERIFICATION SUMMARY:")
    all_passed = all(results.values())
    for k, v in results.items():
        print(f" - {k:<20}: {'PASS' if v else 'FAIL'}")
    print(f"\nOVERALL RESULT: {'ALL PASS' if all_passed else 'FAILURES DETECTED'}")
    print("=" * 60)
    return all_passed

if __name__ == "__main__":
    run_live_api_tests()
