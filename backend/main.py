import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from routes import photo_upload, qa_pack, inspection, case_management, static_routes, file_routes
from routes.photo_upload import router as photo_upload_router
from routes.qa_pack import router as qa_pack_router
from routes.analyze import router as analyze_router
# importing relevant tools

app = FastAPI(
    title="BrazeUp MVP API",
    description="Metal defect detection API",
    version="1.0.0"
)
# making FastAPI app 

# manual cors 
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # allows all origins 
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




app.include_router(analyze_router, prefix="/api") # registering analyze router
app.include_router(qa_pack_router, prefix="/api", tags=["QA-pack ZIP Bundler"])  
app.include_router(photo_upload_router, prefix="/api", tags=["upload"])  

@app.get("/health")
def health():
    return {"status": "healthy"}

# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 5000 reminder on how to run
