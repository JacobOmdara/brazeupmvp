from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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
app.include_router(analyze_router, prefix="/api") # registering analyze router
app.include_router(qa_pack_router, prefix="/api", tags=["QA-pack ZIP Bundler"])  
app.include_router(photo_upload_router, prefix="/api", tags=["upload"])  

@app.get("/health")
def health():
    return {"status": "healthy"}

# Run with: uvicorn main:app --reload --host 0.0.0.0 --port 5000 reminder on how to run