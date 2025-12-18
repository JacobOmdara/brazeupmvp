"""
Service layer for inspection form submissions
"""
from fastapi import UploadFile, HTTPException
from typing import List
import json
import os
from datetime import datetime


class InspectionService:
    """Handle inspection form business logic"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def validate_photos(self, photos: List[UploadFile]) -> None:
        """Validate photo count"""
        if len(photos) < 3 or len(photos) > 6:
            raise HTTPException(
                status_code=400, 
                detail="Please upload 3-6 photos"
            )
    
    def validate_consent(self, consent: bool) -> None:
        """Validate consent checkbox"""
        if not consent:
            raise HTTPException(
                status_code=400, 
                detail="Consent is required"
            )
    
    async def save_photos(
        self, 
        photos: List[UploadFile], 
        submission_dir: str
    ) -> List[str]:
        """Save uploaded photos to disk"""
        photo_paths = []
        
        for idx, photo in enumerate(photos):
            file_path = f"{submission_dir}/photo_{idx+1}_{photo.filename}"
            
            with open(file_path, "wb") as f:
                content = await photo.read()
                f.write(content)
            
            photo_paths.append(file_path)
        
        return photo_paths
    
    def create_submission_data(
        self,
        submission_id: str,
        part_family: str,
        alloy: str,
        damage_type: str,
        gap_estimate: str,  # Changed from float to str
        length_estimate: str,  # Changed from float to str
        consent: bool,
        photo_paths: List[str]
    ) -> dict:
        """Create submission data dictionary"""
        return {
            "submission_id": submission_id,
            "timestamp": datetime.now().isoformat(),
            "part_family": part_family,
            "alloy": alloy,
            "damage_type": damage_type,
            "gap_estimate": gap_estimate,
            "length_estimate": length_estimate,
            "consent": consent,
            "photo_paths": photo_paths
        }
    
    def save_submission_metadata(
        self, 
        submission_dir: str, 
        form_data: dict
    ) -> None:
        """Save form data to JSON file"""
        with open(f"{submission_dir}/submission_data.json", "w") as f:
            json.dump(form_data, f, indent=2)
    
    async def process_inspection(
        self,
        part_family: str,
        alloy: str,
        damage_type: str,
        gap_estimate: str,
        length_estimate: str,
        consent: bool,
        photos: List[UploadFile]
    ) -> dict:
        """
        Main method to process inspection submission
        """
        # Validate inputs
        self.validate_photos(photos)
        self.validate_consent(consent)
        
        # Create unique submission ID and directory
        submission_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        submission_dir = f"{self.upload_dir}/{submission_id}"
        os.makedirs(submission_dir, exist_ok=True)
        
        # Save photos
        photo_paths = await self.save_photos(photos, submission_dir)
        
        # Create form data
        form_data = self.create_submission_data(
            submission_id=submission_id,
            part_family=part_family,
            alloy=alloy,
            damage_type=damage_type,
            gap_estimate=gap_estimate,
            length_estimate=length_estimate,
            consent=consent,
            photo_paths=photo_paths
        )
        
        # Save metadata
        self.save_submission_metadata(submission_dir, form_data)
        
        return {
            "status": "success",
            "message": "Inspection submitted successfully",
            "submission_id": submission_id,
            "data": form_data
        }
    
    def get_all_submissions(self) -> List[dict]:
        """Retrieve all submissions"""
        submissions = []
        
        if os.path.exists(self.upload_dir):
            for submission_id in os.listdir(self.upload_dir):
                json_path = f"{self.upload_dir}/{submission_id}/submission_data.json"
                
                if os.path.exists(json_path):
                    with open(json_path, "r") as f:
                        submissions.append(json.load(f))
        
        return submissions