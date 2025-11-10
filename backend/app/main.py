from fastapi import FastAPI
from app.routers import photo_upload, qa_pack


app = FastAPI(title="Braze Up MVP", version="1.0.0")

app.include_router(qa_pack.router, prefix="/api/v1", tags=["QA-pack ZIP Bundler"])  # API version prefix
app.include_router(photo_upload.router, prefix="/api/v1", tags=["upload"])  # API version prefix

@app.get("/health_endpoint")
async def root():
    return {"message": "Status OK!"}

@app.get("/")
async def root():
    return {"message": "Server Started!"}