from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from typing import List
import json
import os
from datetime import datetime

from app.routers import photo_upload, qa_pack

app = FastAPI(title="Braze Up MVP", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create uploads directory if it doesn't exist
os.makedirs("uploads", exist_ok=True)

# Include existing routers
app.include_router(qa_pack.router, prefix="/api/v1", tags=["QA-pack ZIP Bundler"])
app.include_router(photo_upload.router, prefix="/api/v1", tags=["upload"])

# Serve the inspection form at root
@app.get("/", response_class=HTMLResponse)
async def serve_form():
    try:
        with open("static/form.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Form not found</h1><p>Please create static/form.html</p>",
            status_code=404
        )

@app.get("/health_endpoint")
async def health():
    return {"message": "Status OK!"}

# NEW: Inspection form submission endpoint
@app.post("/api/submit-inspection")
async def submit_inspection(
    part_family: str = Form(...),
    alloy: str = Form(...),
    damage_type: str = Form(...),
    gap_estimate: float = Form(...),
    length_estimate: float = Form(...),
    consent: bool = Form(...),
    photos: List[UploadFile] = File(...)
):
    """
    Handle the multi-step form submission
    """
    # Validate photo count
    if len(photos) < 3 or len(photos) > 6:
        raise HTTPException(status_code=400, detail="Please upload 3-6 photos")
    
    # Validate consent
    if not consent:
        raise HTTPException(status_code=400, detail="Consent is required")
    
    # Create a unique submission ID
    submission_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    submission_dir = f"uploads/{submission_id}"
    os.makedirs(submission_dir, exist_ok=True)
    
    # Save photos
    photo_paths = []
    for idx, photo in enumerate(photos):
        file_path = f"{submission_dir}/photo_{idx+1}_{photo.filename}"
        with open(file_path, "wb") as f:
            content = await photo.read()
            f.write(content)
        photo_paths.append(file_path)
    
    # Save form data
    form_data = {
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
    
    # Save to JSON file
    with open(f"{submission_dir}/submission_data.json", "w") as f:
        json.dump(form_data, f, indent=2)
    
    return {
        "status": "success",
        "message": "Inspection submitted successfully",
        "submission_id": submission_id,
        "data": form_data
    }

# Optional: Endpoint to retrieve submissions
@app.get("/api/submissions")
async def get_submissions():
    """Get all submissions"""
    submissions = []
    if os.path.exists("uploads"):
        for submission_id in os.listdir("uploads"):
            json_path = f"uploads/{submission_id}/submission_data.json"
            if os.path.exists(json_path):
                with open(json_path, "r") as f:
                    submissions.append(json.load(f))
    return {"submissions": submissions}