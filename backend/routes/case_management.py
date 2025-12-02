"""
Router for case management endpoints
"""
from fastapi import APIRouter, HTTPException
from typing import Optional

from app.services.case_service import CaseService, CaseStatus

router = APIRouter()
case_service = CaseService()


@router.get("/cases")
async def get_cases(status: Optional[str] = None):
    """
    Get all cases or filter by status
    
    - **status**: Optional filter (pending, analyzed, completed)
    """
    if status:
        try:
            case_status = CaseStatus(status.lower())
            cases = case_service.get_cases_by_status(case_status)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid status. Must be one of: {', '.join([s.value for s in CaseStatus])}"
            )
    else:
        cases = case_service.get_all_cases()
    
    return {
        "cases": cases,
        "count": len(cases)
    }


@router.get("/cases/{case_id}")
async def get_case_detail(case_id: str):
    """
    Get detailed information for a specific case
    
    - **case_id**: The unique case identifier
    """
    case = case_service.get_case_by_id(case_id)
    
    if not case:
        raise HTTPException(
            status_code=404, 
            detail=f"Case {case_id} not found"
        )
    
    return case


@router.patch("/cases/{case_id}/status")
async def update_case_status(case_id: str, status: str):
    """
    Update the status of a case
    
    - **case_id**: The unique case identifier
    - **status**: New status (pending, analyzed, completed)
    """
    try:
        case_status = CaseStatus(status.lower())
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid status. Must be one of: {', '.join([s.value for s in CaseStatus])}"
        )
    
    updated_case = case_service.update_case_status(case_id, case_status)
    
    if not updated_case:
        raise HTTPException(
            status_code=404,
            detail=f"Case {case_id} not found"
        )
    
    return {
        "message": "Case status updated successfully",
        "case": updated_case
    }


@router.get("/cases/statistics/summary")
async def get_case_statistics():
    """
    Get statistics about all cases
    """
    stats = case_service.get_case_statistics()
    return stats