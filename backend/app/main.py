import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.routers import photo_upload, qa_pack, inspection, case_management

app = FastAPI(title="Braze Up MVP", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(qa_pack.router, prefix="/api/v1", tags=["QA-pack ZIP Bundler"])
app.include_router(photo_upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(inspection.router, prefix="/api", tags=["inspection"])
app.include_router(case_management.router, prefix="/api", tags=["cases"])


@app.get("/", response_class=HTMLResponse)
async def serve_form():
    """Serve the inspection form"""
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
    """Health check endpoint"""
    return {"message": "Status OK!"}


@app.get("/uploads/{case_id}/{filename}")
async def get_photo(case_id: str, filename: str):
    """Serve uploaded photos"""
    file_path = f"uploads/{case_id}/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise Exception(status_code=404, detail="Photo not found")

@app.get("/dashboard", response_class=HTMLResponse)
async def serve_dashboard():
    """Serve the case management dashboard"""
    try:
        with open("static/dashboard.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Dashboard not found</h1>",
            status_code=404
        )
    

@app.get("/photo-viewer", response_class=HTMLResponse)
async def serve_photo_viewer():
    """Serve the photo viewer with mask overlay"""
    try:
        with open("static/photo-viewer.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Photo viewer not found</h1>",
            status_code=404
        )
    
@app.get("/masks/{case_id}/{filename}")
async def get_mask(case_id: str, filename: str):
    """Serve segmentation masks"""
    # Assuming masks are stored in uploads/{case_id}/masks/
    file_path = f"uploads/{case_id}/masks/{filename}"
    if os.path.exists(file_path):
        return FileResponse(file_path)
    raise Exception(status_code=404, detail="Mask not found")