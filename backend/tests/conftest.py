"""
Pytest configuration and fixtures for backend tests
"""
import os
import shutil
import pytest
from fastapi.testclient import TestClient

# Set test upload directory before importing app
os.environ["UPLOAD_DIR"] = "tests/test_uploads"

from main import app


@pytest.fixture(scope="session")
def test_client():
    """Create a test client for the FastAPI app"""
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="function")
def clean_test_uploads():
    """Clean up test uploads directory before and after each test"""
    # Use the same directory that services use
    test_upload_dir = "uploads"
    
    # Backup existing uploads if any
    backup_dir = "uploads_backup"
    had_existing = False
    if os.path.exists(test_upload_dir):
        had_existing = True
        if os.path.exists(backup_dir):
            shutil.rmtree(backup_dir)
        shutil.move(test_upload_dir, backup_dir)
    
    os.makedirs(test_upload_dir, exist_ok=True)
    
    yield test_upload_dir
    
    # Clean after test
    if os.path.exists(test_upload_dir):
        shutil.rmtree(test_upload_dir)
    
    # Restore backup if existed
    if had_existing and os.path.exists(backup_dir):
        shutil.move(backup_dir, test_upload_dir)


@pytest.fixture
def sample_image_path():
    """Return path to a sample test image"""
    return "tests/qa_test/images/test1.jpg"


@pytest.fixture
def sample_images():
    """Return list of sample test image paths"""
    return [
        "tests/qa_test/images/test1.jpg",
        "tests/qa_test/images/test2.jpg",
        "tests/qa_test/images/test3.jpg",
    ]


@pytest.fixture
def valid_inspection_form_data():
    """Return valid form data for inspection submission"""
    return {
        "part_family": "H",
        "alloy": "A356",
        "damage_type": "crack",
        "gap_estimate": "1mm",
        "length_estimate": "20mm",
        "consent": "true",
    }
