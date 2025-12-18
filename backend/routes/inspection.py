from fastapi import APIRouter, Form, UploadFile, File, HTTPException, status
from typing import List
from services.inspection import InspectionService

router = APIRouter()
inspection_service = InspectionService()


@router.post(
    "/submit-inspection",
    status_code=status.HTTP_200_OK,
    summary="Submit an inspection form with photos",
)
async def submit_inspection(
    part_family: str = Form(...),
    alloy: str = Form(...),
    damage_type: str = Form(...),
    gap_estimate: str = Form(...),  # Changed from float to str
    length_estimate: str = Form(...),  # Changed from float to str
    consent: bool = Form(...),
    photos: List[UploadFile] = File(...),
):
    """Endpoint to accept an inspection form and save photos/metadata."""
    try:
        result = await inspection_service.process_inspection(
            part_family=part_family,
            alloy=alloy,
            damage_type=damage_type,
            gap_estimate=gap_estimate,
            length_estimate=length_estimate,
            consent=consent,
            photos=photos,
        )
        return result
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))