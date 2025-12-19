from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter()


@router.get("/", response_class=HTMLResponse)
async def serve_home():
    """Serve the inspection form as homepage"""
    try:
        with open("static/form.html", "r") as f:
            return f.read()
    except FileNotFoundError:
        return HTMLResponse(
            content="<h1>Welcome to Tapestic</h1><p><a href='/form'>Go to Form</a> | <a href='/dashboard'>Go to Dashboard</a></p>",
            status_code=200
        )

@router.get("/form", response_class=HTMLResponse)
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

@router.get("/dashboard", response_class=HTMLResponse)
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

@router.get("/photo-viewer", response_class=HTMLResponse)
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