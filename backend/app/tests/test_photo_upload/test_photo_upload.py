from fastapi.testclient import TestClient
from fastapi import UploadFile
import pytest
import io
import os
from unittest.mock import Mock, patch

# Assuming your FastAPI app is defined in main.py
# from main import app
# client = TestClient(app)

def create_mock_upload_file(filename: str, content: bytes, content_type: str):
    """Helper function to create mock UploadFile objects for testing."""
    file = Mock(spec=UploadFile)
    file.filename = filename
    file.content_type = content_type
    file.read = Mock(return_value=content)
    file.seek = Mock()
    return file

# Test data helpers
def create_valid_image_content(size_mb: float = 1) -> bytes:
    """Create mock image content of specified size."""
    return b"fake_image_data" * int((size_mb * 1024 * 1024) / 15)

def create_oversized_image_content() -> bytes:
    """Create mock image content larger than 10MB."""
    return b"x" * (11 * 1024 * 1024)

# =============================================================================
# API ENDPOINT TESTS (using TestClient)
# =============================================================================

@pytest.mark.asyncio
async def test_upload_valid_photos():
    """Test uploading valid number of JPG photos (3-6 images)."""
    files = [
        ("files", ("photo1.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg")),
        ("files", ("photo2.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg")),
        ("files", ("photo3.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg")),
    ]
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 200
    assert "image_urls" in response.json()
    assert len(response.json()["image_urls"]) == 3

@pytest.mark.asyncio
async def test_upload_valid_png_photos():
    """Test uploading valid PNG photos."""
    files = [
        ("files", ("photo1.png", io.BytesIO(create_valid_image_content()), "image/png")),
        ("files", ("photo2.png", io.BytesIO(create_valid_image_content()), "image/png")),
        ("files", ("photo3.png", io.BytesIO(create_valid_image_content()), "image/png")),
    ]
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_upload_maximum_photos():
    """Test uploading maximum allowed photos (6)."""
    files = [
        ("files", (f"photo{i}.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg"))
        for i in range(1, 7)
    ]
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 200
    assert len(response.json()["image_urls"]) == 6

@pytest.mark.asyncio
async def test_upload_invalid_count_too_few():
    """Test uploading too few photos (1-2, should fail with min 3)."""
    files = [
        ("files", ("photo1.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg")),
    ]
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 400
    assert "between 3 and 6" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_invalid_count_too_many():
    """Test uploading too many photos (7+, should fail with max 6)."""
    files = [
        ("files", (f"photo{i}.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg"))
        for i in range(1, 8)
    ]
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 400
    assert "between 3 and 6" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_oversized_file():
    """Test uploading file > 10MB (should return 400)."""
    files = [
        ("files", ("photo1.jpg", io.BytesIO(create_oversized_image_content()), "image/jpeg")),
        ("files", ("photo2.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg")),
        ("files", ("photo3.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg")),
    ]
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 400
    assert "exceeds 10MB limit" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_invalid_format():
    """Test uploading unsupported file format (.pdf instead of .jpg)."""
    files = [
        ("files", ("document.pdf", io.BytesIO(b"fake_pdf_content"), "application/pdf")),
        ("files", ("photo2.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg")),
        ("files", ("photo3.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg")),
    ]
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 400
    assert "must be JPEG or PNG" in response.json()["detail"]

@pytest.mark.asyncio
async def test_upload_mixed_valid_formats():
    """Test uploading mix of JPEG and PNG files."""
    files = [
        ("files", ("photo1.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg")),
        ("files", ("photo2.png", io.BytesIO(create_valid_image_content()), "image/png")),
        ("files", ("photo3.jpg", io.BytesIO(create_valid_image_content()), "image/jpeg")),
    ]
    
    response = client.post("/upload", files=files)
    
    assert response.status_code == 200

# =============================================================================
# UNIT TESTS FOR PhotoService
# =============================================================================

@pytest.mark.asyncio
async def test_validate_files_success():
    """Test validation passes for valid files."""
    from photo_service import PhotoService
    
    service = PhotoService()
    files = [
        create_mock_upload_file("photo1.jpg", create_valid_image_content(), "image/jpeg"),
        create_mock_upload_file("photo2.jpg", create_valid_image_content(), "image/jpeg"),
        create_mock_upload_file("photo3.jpg", create_valid_image_content(), "image/jpeg"),
    ]
    
    # Should not raise any exception
    await service.validate_files(files)

@pytest.mark.asyncio
async def test_validate_files_too_few():
    """Test validation fails with fewer than 3 files."""
    from photo_service import PhotoService
    from fastapi import HTTPException
    
    service = PhotoService()
    files = [
        create_mock_upload_file("photo1.jpg", create_valid_image_content(), "image/jpeg"),
        create_mock_upload_file("photo2.jpg", create_valid_image_content(), "image/jpeg"),
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        await service.validate_files(files)
    
    assert exc_info.value.status_code == 400
    assert "between 3 and 6" in exc_info.value.detail

@pytest.mark.asyncio
async def test_validate_files_too_many():
    """Test validation fails with more than 6 files."""
    from photo_service import PhotoService
    from fastapi import HTTPException
    
    service = PhotoService()
    files = [
        create_mock_upload_file(f"photo{i}.jpg", create_valid_image_content(), "image/jpeg")
        for i in range(7)
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        await service.validate_files(files)
    
    assert exc_info.value.status_code == 400
    assert "between 3 and 6" in exc_info.value.detail

@pytest.mark.asyncio
async def test_validate_files_invalid_type():
    """Test validation fails with invalid file type."""
    from photo_service import PhotoService
    from fastapi import HTTPException
    
    service = PhotoService()
    files = [
        create_mock_upload_file("photo1.jpg", create_valid_image_content(), "image/jpeg"),
        create_mock_upload_file("document.pdf", b"pdf_content", "application/pdf"),
        create_mock_upload_file("photo3.jpg", create_valid_image_content(), "image/jpeg"),
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        await service.validate_files(files)
    
    assert exc_info.value.status_code == 400
    assert "must be JPEG or PNG" in exc_info.value.detail

@pytest.mark.asyncio
async def test_validate_files_oversized():
    """Test validation fails with file exceeding size limit."""
    from photo_service import PhotoService
    from fastapi import HTTPException
    
    service = PhotoService()
    files = [
        create_mock_upload_file("photo1.jpg", create_valid_image_content(), "image/jpeg"),
        create_mock_upload_file("photo2.jpg", create_oversized_image_content(), "image/jpeg"),
        create_mock_upload_file("photo3.jpg", create_valid_image_content(), "image/jpeg"),
    ]
    
    with pytest.raises(HTTPException) as exc_info:
        await service.validate_files(files)
    
    assert exc_info.value.status_code == 400
    assert "exceeds 10MB limit" in exc_info.value.detail

@pytest.mark.asyncio
async def test_save_files_creates_unique_filenames():
    """Test that saved files have unique filenames."""
    from photo_service import PhotoService
    
    service = PhotoService()
    files = [
        create_mock_upload_file("photo.jpg", create_valid_image_content(), "image/jpeg"),
        create_mock_upload_file("photo.jpg", create_valid_image_content(), "image/jpeg"),
        create_mock_upload_file("photo.jpg", create_valid_image_content(), "image/jpeg"),
    ]
    
    with patch('aiofiles.open'):
        saved_paths = await service.save_files(files)
    
    # Check all paths are unique
    assert len(saved_paths) == len(set(saved_paths))
    
    # Check all paths end with correct extension
    assert all(path.endswith('.jpg') for path in saved_paths)

@pytest.mark.asyncio
async def test_save_files_preserves_extension():
    """Test that file extensions are preserved."""
    from photo_service import PhotoService
    
    service = PhotoService()
    files = [
        create_mock_upload_file("photo1.jpg", create_valid_image_content(), "image/jpeg"),
        create_mock_upload_file("photo2.png", create_valid_image_content(), "image/png"),
        create_mock_upload_file("photo3.jpeg", create_valid_image_content(), "image/jpeg"),
    ]
    
    with patch('aiofiles.open'):
        saved_paths = await service.save_files(files)
    
    assert saved_paths[0].endswith('.jpg')
    assert saved_paths[1].endswith('.png')
    assert saved_paths[2].endswith('.jpeg')

@pytest.mark.asyncio
async def test_upload_directory_created():
    """Test that upload directory is created on initialization."""
    from photo_service import PhotoService
    
    with patch('os.makedirs') as mock_makedirs:
        service = PhotoService()
        mock_makedirs.assert_called_once_with("storage/uploads", exist_ok=True)