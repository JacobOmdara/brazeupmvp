from fastapi import APIRouter, UploadFile, File, HTTPException
import sys 
sys.path.append('..')

from services.ml_wrapper import predict_defects

router = APIRouter()

@router.post("/analyze")
async def analyze(image: UploadFile = File(...)):
    if not image:
        raise HTTPException(status_code=400, detail="No image provided")
    
    if not image.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    try: 
        image_bytes = await image.read()
        defects = predict_defects(image_bytes)
        return {"success": True, "defects": defects}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))