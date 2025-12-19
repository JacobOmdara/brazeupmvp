"""
Tests for case management endpoints
"""
import os
import json
import shutil
import pytest


class TestGetCases:
    """Test suite for GET /api/cases endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_test_cases(self, clean_test_uploads):
        """Set up test cases before each test"""
        self.upload_dir = clean_test_uploads
        
        # Create sample cases
        case1_dir = os.path.join(self.upload_dir, "20251201_120000")
        case2_dir = os.path.join(self.upload_dir, "20251202_130000")
        
        os.makedirs(case1_dir, exist_ok=True)
        os.makedirs(case2_dir, exist_ok=True)
        
        # Case 1 - pending
        with open(os.path.join(case1_dir, "submission_data.json"), "w") as f:
            json.dump({
                "submission_id": "20251201_120000",
                "timestamp": "2025-12-01T12:00:00",
                "part_family": "H",
                "alloy": "A356",
                "damage_type": "crack",
                "gap_estimate": "1mm",
                "length_estimate": "20mm",
                "status": "pending",
                "photo_paths": ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
            }, f)
        
        # Case 2 - analyzed
        with open(os.path.join(case2_dir, "submission_data.json"), "w") as f:
            json.dump({
                "submission_id": "20251202_130000",
                "timestamp": "2025-12-02T13:00:00",
                "part_family": "G",
                "alloy": "B356",
                "damage_type": "erosion",
                "gap_estimate": "2mm",
                "length_estimate": "30mm",
                "status": "analyzed",
                "photo_paths": ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
            }, f)
        
        yield
    
    def test_get_all_cases(self, test_client):
        """Test retrieving all cases"""
        response = test_client.get("/api/cases")
        
        assert response.status_code == 200
        data = response.json()
        assert "cases" in data
        assert "count" in data
    
    def test_get_cases_filter_by_status(self, test_client):
        """Test filtering cases by status"""
        response = test_client.get("/api/cases?status=pending")
        
        assert response.status_code == 200
        data = response.json()
        assert "cases" in data
    
    def test_get_cases_invalid_status(self, test_client):
        """Test filtering with invalid status returns error"""
        response = test_client.get("/api/cases?status=invalid_status")
        
        assert response.status_code == 400
        assert "Invalid status" in response.json()["detail"]


class TestGetCaseDetail:
    """Test suite for GET /api/cases/{case_id} endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_test_case(self, clean_test_uploads):
        """Set up a test case before each test"""
        self.upload_dir = clean_test_uploads
        self.case_id = "20251201_120000"
        case_dir = os.path.join(self.upload_dir, self.case_id)
        
        os.makedirs(case_dir, exist_ok=True)
        
        with open(os.path.join(case_dir, "submission_data.json"), "w") as f:
            json.dump({
                "submission_id": self.case_id,
                "timestamp": "2025-12-01T12:00:00",
                "part_family": "H",
                "alloy": "A356",
                "damage_type": "crack",
                "gap_estimate": "1mm",
                "length_estimate": "20mm",
                "status": "pending",
                "photo_paths": ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
            }, f)
        
        yield
    
    def test_get_case_detail_success(self, test_client):
        """Test retrieving a specific case"""
        response = test_client.get(f"/api/cases/{self.case_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["submission_id"] == self.case_id
        assert data["part_family"] == "H"
    
    def test_get_case_detail_not_found(self, test_client):
        """Test retrieving non-existent case returns 404"""
        response = test_client.get("/api/cases/nonexistent_case_id")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]


class TestUpdateCaseStatus:
    """Test suite for PATCH /api/cases/{case_id}/status endpoint"""
    
    @pytest.fixture(autouse=True)
    def setup_test_case(self, clean_test_uploads):
        """Set up a test case before each test"""
        self.upload_dir = clean_test_uploads
        self.case_id = "20251201_120000"
        case_dir = os.path.join(self.upload_dir, self.case_id)
        
        os.makedirs(case_dir, exist_ok=True)
        
        with open(os.path.join(case_dir, "submission_data.json"), "w") as f:
            json.dump({
                "submission_id": self.case_id,
                "timestamp": "2025-12-01T12:00:00",
                "part_family": "H",
                "alloy": "A356",
                "damage_type": "crack",
                "gap_estimate": "1mm",
                "length_estimate": "20mm",
                "status": "pending",
                "photo_paths": ["photo1.jpg", "photo2.jpg", "photo3.jpg"]
            }, f)
        
        yield
    
    def test_update_case_status_success(self, test_client):
        """Test updating case status"""
        response = test_client.patch(
            f"/api/cases/{self.case_id}/status?status=analyzed"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Case status updated successfully"
    
    def test_update_case_status_invalid(self, test_client):
        """Test updating with invalid status returns error"""
        response = test_client.patch(
            f"/api/cases/{self.case_id}/status?status=invalid"
        )
        
        assert response.status_code == 400
        assert "Invalid status" in response.json()["detail"]
    
    def test_update_case_status_not_found(self, test_client):
        """Test updating non-existent case returns 404"""
        response = test_client.patch(
            "/api/cases/nonexistent_case/status?status=analyzed"
        )
        
        assert response.status_code == 404


class TestCaseStatistics:
    """Test suite for GET /api/cases/statistics/summary endpoint"""
    
    def test_get_case_statistics(self, test_client, clean_test_uploads):
        """Test retrieving case statistics"""
        response = test_client.get("/api/cases/statistics/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "total" in data
        assert "pending" in data
        assert "analyzed" in data
        assert "completed" in data
