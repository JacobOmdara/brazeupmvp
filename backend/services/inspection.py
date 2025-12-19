"""
Service layer for inspection form submissions
"""
from fastapi import UploadFile, HTTPException
from typing import List
import json
import os
from datetime import datetime
from services.ml_wrapper import predict_defects

# Defect solutions mapping
DEFECT_SOLUTIONS = {
    "crazing": {
        "severity": "Medium",
        "description": "Fine network of surface cracks caused by thermal stress or coating issues",
        "solutions": [
            "Surface grinding to remove affected layer",
            "Stress relief heat treatment",
            "Re-coating with compatible material",
            "Controlled cooling process adjustment"
        ],
        "estimated_repair_time": "2-4 hours"
    },
    "inclusion": {
        "severity": "High",
        "description": "Foreign material embedded in the metal surface during manufacturing",
        "solutions": [
            "Localized grinding to remove inclusion",
            "Weld repair if depth permits",
            "Part replacement if structural integrity compromised",
            "Non-destructive testing after repair"
        ],
        "estimated_repair_time": "4-8 hours"
    },
    "scratches": {
        "severity": "Low",
        "description": "Surface marks from mechanical contact or handling",
        "solutions": [
            "Fine polishing with appropriate abrasive",
            "Surface refinishing",
            "Protective coating application",
            "Review handling procedures"
        ],
        "estimated_repair_time": "1-2 hours"
    },
    "pitted_surface": {
        "severity": "Medium-High",
        "description": "Localized corrosion creating small cavities in the surface",
        "solutions": [
            "Chemical treatment to neutralize corrosion",
            "Filling with compatible filler material",
            "Surface resurfacing and sealing",
            "Environmental protection measures"
        ],
        "estimated_repair_time": "3-6 hours"
    },
    "rolled-in_scale": {
        "severity": "Medium",
        "description": "Oxide scale pressed into surface during rolling process",
        "solutions": [
            "Mechanical descaling (shot blasting)",
            "Chemical pickling treatment",
            "Surface grinding if severe",
            "Process parameter adjustment for prevention"
        ],
        "estimated_repair_time": "2-4 hours"
    },
    "patches": {
        "severity": "Medium",
        "description": "Irregular surface areas with different properties than surrounding material",
        "solutions": [
            "Weld overlay repair",
            "Patch grinding and blending",
            "Heat treatment for uniformity",
            "Material analysis to determine cause"
        ],
        "estimated_repair_time": "3-5 hours"
    }
}


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
    
    def analyze_photos(self, photo_paths: List[str]) -> dict:
        """Run ML analysis on all photos and aggregate results"""
        all_defects = []
        photo_analysis = []
        analysis_successful = True
        
        try:
            for photo_path in photo_paths:
                try:
                    with open(photo_path, "rb") as f:
                        image_bytes = f.read()
                    
                    defects = predict_defects(image_bytes)
                    photo_analysis.append({
                        "photo": os.path.basename(photo_path),
                        "defects_found": len(defects),
                        "defects": defects
                    })
                    all_defects.extend(defects)
                except Exception as e:
                    print(f"Error analyzing {photo_path}: {e}")
                    photo_analysis.append({
                        "photo": os.path.basename(photo_path),
                        "error": str(e),
                        "defects": []
                    })
        except Exception as e:
            print(f"ML Analysis failed: {e}")
            analysis_successful = False
            return {
                "total_defects_found": 0,
                "defect_summary": {},
                "photo_analysis": [],
                "analysis_status": "failed",
                "error": str(e)
            }
        
        # Aggregate defect types with their confidence scores
        defect_summary = {}
        defect_confidences = {}
        
        for defect in all_defects:
            defect_type = defect.get("type", "unknown")
            defect_conf = defect.get("confidence", 0)
            
            if defect_type not in defect_summary:
                defect_summary[defect_type] = 0
                defect_confidences[defect_type] = []
            
            defect_summary[defect_type] += 1
            defect_confidences[defect_type].append(defect_conf)
        
        # Find the primary (most common) defect type
        primary_defect = None
        primary_count = 0
        for defect_type, count in defect_summary.items():
            if count > primary_count:
                primary_defect = defect_type
                primary_count = count
        
        # Calculate confidence as average model confidence for primary defect regions
        if primary_defect and defect_confidences.get(primary_defect):
            confidence = round(sum(defect_confidences[primary_defect]) / len(defect_confidences[primary_defect]), 1)
        else:
            confidence = 0
        
        # Get solution for primary defect
        solution = DEFECT_SOLUTIONS.get(primary_defect, {}) if primary_defect else {}
        
        return {
            "primary_defect": primary_defect or "none",
            "confidence": confidence,
            "total_regions_analyzed": len(all_defects),
            "defect_summary": defect_summary,
            "photo_analysis": photo_analysis,
            "analysis_status": "completed",
            "recommended_solution": solution
        }

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
        
        # Create form data first (so we don't lose it if analysis fails)
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
        
        # Try to run ML analysis (but don't fail if it doesn't work)
        try:
            print(f"Starting ML analysis for {submission_id}...")
            analysis_results = self.analyze_photos(photo_paths)
            
            if analysis_results.get("analysis_status") == "completed":
                form_data["status"] = "analyzed"
                form_data["analyzed_at"] = datetime.now().isoformat()
                form_data["analysis_results"] = analysis_results
                message = "Inspection submitted and analyzed successfully"
            else:
                form_data["status"] = "pending"
                form_data["analysis_results"] = analysis_results
                message = "Inspection submitted. Analysis pending."
        except Exception as e:
            print(f"Analysis failed: {e}")
            form_data["status"] = "pending"
            form_data["analysis_error"] = str(e)
            analysis_results = {"error": str(e)}
            message = "Inspection submitted. Analysis will be done later."
        
        # Save metadata
        self.save_submission_metadata(submission_dir, form_data)
        
        return {
            "status": "success",
            "message": message,
            "submission_id": submission_id,
            "analysis": analysis_results,
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