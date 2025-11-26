from fastapi import APIRouter, UploadFile, File, HTTPException, status, Query
from typing import List, Optional
from services.photo_upload import photo_service

router = APIRouter()

@router.post(
    "/upload",
    status_code=status.HTTP_201_CREATED,
    summary="Upload defect photos for analysis",
    description="""
    Upload 3-6 photos of metal defects for AI analysis.
    
    **Requirements:**
    - 3-6 images required (1-6 in test mode)
    - JPEG or PNG formats only  
    - Max 10MB per file
    - Include multiple angles of defects
    - One photo should contain scale reference (ruler/coin)
    
    **Test Mode:**
    - Set test=true to reduce minimum files to 1 for testing
    """,
)
async def upload_defect_photos(
    files: List[UploadFile] = File(...),
    test: Optional[bool] = Query(False, description="Test mode: reduces minimum file requirement to 1")
):
    """
    Upload photos specifically for metal defect analysis pipeline.

    Validates and stores photos that will be processed by the AI model
    to detect cracks, edge wear, pits, and other defects in aerospace components.
    
    Args:
        files: List of uploaded image files
        test: If True, reduces minimum file requirement to 1 for testing
    """
    
    # Validate files against business rules
    await photo_service.validate_files(files, test=test)

    # Save files to storage
    image_paths = await photo_service.save_files(files)

    return {
        "message": "Defect photos uploaded successfully and ready for AI analysis",
        "image_paths": image_paths,
        "total_uploaded": len(image_paths),
        "test_mode": test
    }