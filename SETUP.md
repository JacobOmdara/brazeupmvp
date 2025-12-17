# BrazeUp Setup Guide


## Prerequisites
- Python 3.11+ 
- pip
- Git

## Installation

1. Clone Repository 
    git clone https://github.com/JacobOmdara/brazeupmvp.git
    cd brazeupmvp/backend

2. Install Dependencies
    pip install -r requirements.txt

3. Run Server
    python -m uvicorn main:app --reload --host 0.0.0.0 --port 5000

4. Access API's
    - Swagger UI: http://localhost:5000/docs
    - ReDoc: http://localhost:5000/redoc


## Error Handling Reference

| Status | Meaning | Example |
|--------|---------|---------|
| 200 OK | Success | Analysis completed |
| 201 Created | Resource created | Photos uploaded |
| 400 Bad Request | Missing fields | No photos in upload |
| 404 Not Found | Resource doesn't exist | Invalid case_id |
| 500 Server Error | Server issue | Model loading failed |

## Common Issues

**Q: Port 5000 already in use?**
A: `lsof -i :5000` then `kill -9 <PID>`

**Q: ModuleNotFoundError: No module named 'torch'?**
A: `pip install torch torchvision`

**Q: Image not processing?**
A: Check image format is .jpg/.png and <5MB