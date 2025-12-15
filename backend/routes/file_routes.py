import os
from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

@router.get("/uploads/{case_id}/{filename}")
async def get_photo(case_id: str, filename: str):
    """Serve uploaded photos"""
    file_path = f"uploads/{case_id}/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Photo not found")

@router.get("/masks/{case_id}/{filename}")
async def get_mask(case_id: str, filename: str):
    """Serve segmentation masks"""
    file_path = f"uploads/{case_id}/masks/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise HTTPException(status_code=404, detail="Mask not found")