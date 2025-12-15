# BrazeUp API Documentation 

## Overview 
FastAPI backend for a metal surface defect detection using PyTorch UNet model for analysis

## Base URL 
the base URL is here: http://localhost:5000/docs

## Endpoints

### 1. Get /health 
checking health of server, endpoint 
- **Response:** 200 OK 
should return 200 if no errors, 400 on user side 500 on server
- **Body:** '{"status": "healthy"}'
 
### 2. Post /api/upload
Upload metal defect photos for HF ML to analyze and give diagnosis
- **Response:** 201 Created
- **Body:** '{"message": "uploaded", "image_paths": [...], "total_uploaded: 3}'

### 3. POST /api/analyze
Analyze images for metal defects on surface, return type and confidence
- **Response:** 200 OK 
- **Body:** '{"success": true, "defects": [{"type": "crazing", "confidence": 0.985, "boudning_box": [...]}]}'

### 4. GET /api/qa-pack
Create QA pack ZIP bundle with the analysis results
- **Response:** 200 OK 
- **Body:** '{"download_url": "/qa-pack/download/qa_pack.zip"}'

