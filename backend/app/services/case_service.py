"""
Service layer for case management
"""
import os
import json
from typing import List, Optional
from datetime import datetime
from enum import Enum


class CaseStatus(str, Enum):
    PENDING = "pending"
    ANALYZED = "analyzed"
    COMPLETED = "completed"


class CaseService:
    """Handle case management business logic"""
    
    def __init__(self, upload_dir: str = "uploads"):
        self.upload_dir = upload_dir
    
    def get_all_cases(self) -> List[dict]:
        """
        Retrieve all cases with their status and metadata
        """
        cases = []
        
        if not os.path.exists(self.upload_dir):
            return cases
        
        for case_id in os.listdir(self.upload_dir):
            case_path = f"{self.upload_dir}/{case_id}"
            json_path = f"{case_path}/submission_data.json"
            
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    case_data = json.load(f)
                
                # Extract relevant fields and add status
                case_summary = {
                    "case_id": case_data.get("submission_id", case_id),
                    "part_family": case_data.get("part_family"),
                    "alloy": case_data.get("alloy"),
                    "defect_type": case_data.get("damage_type"),
                    "gap_estimate": case_data.get("gap_estimate"),
                    "length_estimate": case_data.get("length_estimate"),
                    "status": case_data.get("status", CaseStatus.PENDING),
                    "created_at": case_data.get("timestamp"),
                    "analyzed_at": case_data.get("analyzed_at"),
                    "completed_at": case_data.get("completed_at"),
                    "photo_count": len(case_data.get("photo_paths", []))
                }
                
                cases.append(case_summary)
        
        # Sort by created_at (newest first)
        cases.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        return cases
    
    def get_case_by_id(self, case_id: str) -> Optional[dict]:
        """
        Retrieve a specific case by ID with full details
        """
        json_path = f"{self.upload_dir}/{case_id}/submission_data.json"
        
        if not os.path.exists(json_path):
            return None
        
        with open(json_path, "r") as f:
            case_data = json.load(f)
        
        # Add status if not present
        if "status" not in case_data:
            case_data["status"] = CaseStatus.PENDING
        
        return case_data
    
    def update_case_status(
        self, 
        case_id: str, 
        status: CaseStatus
    ) -> Optional[dict]:
        """
        Update the status of a case
        """
        json_path = f"{self.upload_dir}/{case_id}/submission_data.json"
        
        if not os.path.exists(json_path):
            return None
        
        with open(json_path, "r") as f:
            case_data = json.load(f)
        
        # Update status
        case_data["status"] = status
        
        # Add timestamp for status change
        timestamp_field = f"{status}_at"
        case_data[timestamp_field] = datetime.now().isoformat()
        
        # Save updated data
        with open(json_path, "w") as f:
            json.dump(case_data, f, indent=2)
        
        return case_data
    
    def get_cases_by_status(self, status: CaseStatus) -> List[dict]:
        """
        Filter cases by status
        """
        all_cases = self.get_all_cases()
        return [case for case in all_cases if case.get("status") == status]
    
    def get_case_statistics(self) -> dict:
        """
        Get statistics about all cases
        """
        all_cases = self.get_all_cases()
        
        stats = {
            "total": len(all_cases),
            "pending": len([c for c in all_cases if c.get("status") == CaseStatus.PENDING]),
            "analyzed": len([c for c in all_cases if c.get("status") == CaseStatus.ANALYZED]),
            "completed": len([c for c in all_cases if c.get("status") == CaseStatus.COMPLETED]),
            "by_part_family": {},
            "by_defect_type": {}
        }
        
        # Count by part family
        for case in all_cases:
            part_family = case.get("part_family", "unknown")
            stats["by_part_family"][part_family] = stats["by_part_family"].get(part_family, 0) + 1
        
        # Count by defect type
        for case in all_cases:
            defect_type = case.get("defect_type", "unknown")
            stats["by_defect_type"][defect_type] = stats["by_defect_type"].get(defect_type, 0) + 1
        
        return stats