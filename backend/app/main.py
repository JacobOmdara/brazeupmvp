from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware

from app.routers import photo_upload, qa_pack, inspection

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