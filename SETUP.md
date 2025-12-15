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