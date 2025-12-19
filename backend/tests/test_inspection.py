"""
Tests for inspection submission endpoints
"""
import os
import pytest


class TestInspectionSubmission:
    """Test suite for POST /api/submit-inspection endpoint"""
    
    def test_submit_inspection_success(
        self,
        test_client, 
        sample_images, 
        valid_inspection_form_data,
        clean_test_uploads
    ):
        """Test successful inspection submission with valid data"""
        # Prepare files
        files = [
            ("photos", (f"test{i+1}.jpg", open(img, "rb"), "image/jpeg"))
            for i, img in enumerate(sample_images)
        ]
        
        try:
            response = test_client.post(
                "/api/submit-inspection",
                data=valid_inspection_form_data,
                files=files,
            )
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert "submission_id" in data
            assert data["message"] == "Inspection submitted successfully"
        finally:
            # Close file handles
            for _, file_tuple in files:
                file_tuple[1].close()
    
    def test_submit_inspection_missing_consent(
        self, 
        test_client, 
        sample_images
    ):
        """Test submission fails when consent is false"""
        files = [
            ("photos", (f"test{i+1}.jpg", open(img, "rb"), "image/jpeg"))
            for i, img in enumerate(sample_images)
        ]
        
        form_data = {
            "part_family": "H",
            "alloy": "A356",
            "damage_type": "crack",
            "gap_estimate": "1mm",
            "length_estimate": "20mm",
            "consent": "false",
        }
        
        try:
            response = test_client.post(
                "/api/submit-inspection",
                data=form_data,
                files=files,
            )
            
            assert response.status_code == 400
            assert "Consent is required" in response.json()["detail"]
        finally:
            for _, file_tuple in files:
                file_tuple[1].close()
    
    def test_submit_inspection_too_few_photos(
        self, 
        test_client, 
        sample_image_path,
        valid_inspection_form_data
    ):
        """Test submission fails with less than 3 photos"""
        # Only 1 photo
        files = [
            ("photos", ("test1.jpg", open(sample_image_path, "rb"), "image/jpeg"))
        ]
        
        try:
            response = test_client.post(
                "/api/submit-inspection",
                data=valid_inspection_form_data,
                files=files,
            )
            
            assert response.status_code == 400
            assert "3-6 photos" in response.json()["detail"]
        finally:
            for _, file_tuple in files:
                file_tuple[1].close()
    
    def test_submit_inspection_too_many_photos(
        self, 
        test_client,
        sample_image_path,
        valid_inspection_form_data
    ):
        """Test submission fails with more than 6 photos"""
        # 7 photos (too many)
        files = [
            ("photos", (f"test{i+1}.jpg", open(sample_image_path, "rb"), "image/jpeg"))
            for i in range(7)
        ]
        
        try:
            response = test_client.post(
                "/api/submit-inspection",
                data=valid_inspection_form_data,
                files=files,
            )
            
            assert response.status_code == 400
            assert "3-6 photos" in response.json()["detail"]
        finally:
            for _, file_tuple in files:
                file_tuple[1].close()
    
    def test_submit_inspection_missing_required_field(
        self, 
        test_client, 
        sample_images
    ):
        """Test submission fails when required field is missing"""
        files = [
            ("photos", (f"test{i+1}.jpg", open(img, "rb"), "image/jpeg"))
            for i, img in enumerate(sample_images)
        ]
        
        # Missing part_family
        form_data = {
            "alloy": "A356",
            "damage_type": "crack",
            "gap_estimate": "1mm",
            "length_estimate": "20mm",
            "consent": "true",
        }
        
        try:
            response = test_client.post(
                "/api/submit-inspection",
                data=form_data,
                files=files,
            )
            
            # FastAPI returns 422 for validation errors
            assert response.status_code == 422
        finally:
            for _, file_tuple in files:
                file_tuple[1].close()
    
    def test_submit_inspection_no_photos(
        self, 
        test_client,
        valid_inspection_form_data
    ):
        """Test submission fails without photos"""
        response = test_client.post(
            "/api/submit-inspection",
            data=valid_inspection_form_data,
        )
        
        # FastAPI returns 422 for missing required files
        assert response.status_code == 422
