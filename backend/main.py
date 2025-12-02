import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from routes import photo_upload, qa_pack, inspection, case_management, static_routes, file_routes

app = FastAPI(title="Braze Up MVP", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health_endpoint")
async def health():
    """Health check endpoint"""
    return {"message": "Status OK!"}

# Include routers
app.include_router(qa_pack.router, prefix="/api/v1", tags=["QA-pack ZIP Bundler"])
app.include_router(photo_upload.router, prefix="/api/v1", tags=["upload"])
app.include_router(inspection.router, prefix="/api", tags=["inspection"])
app.include_router(case_management.router, prefix="/api", tags=["cases"])
app.include_router(static_routes.router, tags=["static"])
app.include_router(file_routes.router, tags=["files"])




