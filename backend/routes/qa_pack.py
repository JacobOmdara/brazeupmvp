from fastapi import APIRouter
from app.services.qa_pack import qa_pack_service
router = APIRouter()


@router.post("/qa-pack")
async def create_qa_pack():
    """
    Create QA pack ZIP bundle and return download URL.
    """
    download_url = qa_pack_service.create_qa_pack()
    return {"download_url": download_url}