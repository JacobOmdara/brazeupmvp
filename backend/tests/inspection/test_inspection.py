import sys
from pathlib import Path
from io import BytesIO
import pytest

# Add BrazeUP and backend directories to path
brazeup_dir = Path(__file__).resolve().parent.parent.parent.parent
backend_dir = brazeup_dir / "backend"

sys.path.insert(0, str(brazeup_dir))
sys.path.insert(0, str(backend_dir))

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def fake_image(name="test.jpg"):
    """Helper to create a fake image file"""
    return (name, BytesIO(b"fake image content"), "image/jpeg")


def test_health_endpoint():
    response = client.get("/health_endpoint")
    assert response.status_code == 200
    assert response.json() == {"message": "Status OK!"}


def test_submit_inspection_success():
    """Submit valid inspection with 3 photos (minimum required)"""
    files = [
        ("photos", fake_image("img1.jpg")),
        ("photos", fake_image("img2.jpg")),
        ("photos", fake_image("img3.jpg")),
    ]
    
    data = {
        "part_family": "H",
        "alloy": "jh",
        "damage_type": "jgh",
        "gap_estimate": "1mm",
        "length_estimate": "20mm",
        "consent": "true"
    }
    
    response = client.post("/api/submit-inspection", data=data, files=files)
    
    assert response.status_code == 200
    json_response = response.json()
    assert json_response["status"] == "success"
    assert "submission_id" in json_response
    assert len(json_response["data"]["photo_paths"]) == 3


def test_submit_inspection_missing_photos():
    """Submit inspection with fewer than 3 photos → should fail"""
    files = [
        ("photos", fake_image("img1.jpg")),
        ("photos", fake_image("img2.jpg")),
    ]
    
    data = {
        "part_family": "H",
        "alloy": "jh",
        "damage_type": "jgh",
        "gap_estimate": "1mm",
        "length_estimate": "20mm",
        "consent": "true"
    }
    
    response = client.post("/api/submit-inspection", data=data, files=files)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Please upload 3-6 photos"


def test_submit_inspection_no_consent():
    """Submit inspection without consent → should fail"""
    files = [
        ("photos", fake_image("img1.jpg")),
        ("photos", fake_image("img2.jpg")),
        ("photos", fake_image("img3.jpg")),
    ]
    
    data = {
        "part_family": "H",
        "alloy": "jh",
        "damage_type": "jgh",
        "gap_estimate": "1mm",
        "length_estimate": "20mm",
        "consent": "false"
    }
    
    response = client.post("/api/submit-inspection", data=data, files=files)
    
    assert response.status_code == 400
    assert response.json()["detail"] == "Consent is required"


def test_submit_inspection_missing_fields():
    """Submit inspection with missing required fields → should fail"""
    files = [
        ("photos", fake_image("img1.jpg")),
        ("photos", fake_image("img2.jpg")),
        ("photos", fake_image("img3.jpg")),
    ]
    
    data = {
        # Missing alloy
        "part_family": "H",
        "damage_type": "jgh",
        "gap_estimate": "1mm",
        "length_estimate": "20mm",
        "consent": "true"
    }
    
    response = client.post("/api/submit-inspection", data=data, files=files)
    
    assert response.status_code == 422  # Unprocessable Entity
