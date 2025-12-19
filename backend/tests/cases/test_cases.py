import sys
from pathlib import Path
brazeup_dir = Path(__file__).resolve().parent.parent.parent.parent
backend_dir = brazeup_dir / "backend"
sys.path.insert(0, str(brazeup_dir))
sys.path.insert(0, str(backend_dir))
from fastapi.testclient import TestClient
from backend.main import app

def test_get_cases_all(): 
    client = TestClient(app) 
    response = client.get("/api/cases") 
    assert response.status_code == 200 
    assert "cases" in response.json() 
    assert "count" in response.json()
    
def test_get_cases_pending():
    client = TestClient(app)
    response = client.get("/api/cases?status=pending")
    assert response.status_code == 200
    assert "cases" in response.json()
    assert "count" in response.json()


def test_get_cases_analyzed():
    client = TestClient(app)
    response = client.get("/api/cases?status=analyzed")
    assert response.status_code == 200
    assert "cases" in response.json()
    assert "count" in response.json()


def test_get_cases_completed():
    client = TestClient(app)
    response = client.get("/api/cases?status=completed")
    assert response.status_code == 200
    assert "cases" in response.json()
    assert "count" in response.json()


def test_invalid_get_cases():
    client = TestClient(app)
    response = client.get("/api/cases?status=invalidstatus")
    assert response.status_code == 400

# def test_patch_case_status():
#     client = TestClient(app)
#     case_id = "20251218_165642"

#     response = client.patch(
#         f"/api/cases/{case_id}/status",
#         json={"status": "completed"}
#     )

#     print(response.json())

#     assert response.status_code == 200
#     assert "case" in response.json()
#     assert response.json()["case"]["status"].lower() == "completed"

# def test_update_case_status_not_found():
#     client = TestClient(app)

#     case_id = "non_existent_case_id"
#     response = client.patch(
#         f"/api/cases/{case_id}/status",
#         json={"status": "completed"}
#     )

#     print(response.text)

#     assert response.status_code == 404
