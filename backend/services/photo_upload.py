import os
import uuid
from fastapi import UploadFile, HTTPException
from typing import List
import aiofiles


class PhotoService:
    """
    Service for handling photo upload validation and storage.
    
    Provides methods to validate file constraints and save uploaded photos
    to local storage with unique filenames.
    """
    def __init__(self):
        self.allowed_types = ["image/jpeg", "image/png"]
        self.max_size = 10 * 1024 * 1024
        self.upload_dir = "storage/uploads"

        # Create upload directory if it doesn't exist
        os.makedirs(self.upload_dir, exist_ok=True)

    async def validate_files(self, files: List[UploadFile]) -> None:
        """
        Validate uploaded files against photo upload specifications.
        
        Validation Rules:
        - File count: 3 minimum, 6 maximum
        - File types: image/jpeg, image/png only
        - File size: 10MB maximum per file
        
        Args:
            files: List of uploaded files to validate
            
        Raises:
            HTTPException: 400 if files violate any validation rules
        """

        # Check number of files
        if len(files) < 3 or len(files) > 6:
            raise HTTPException(
                status_code=400, detail="You must upload between 3 and 6 images"
            )

        # Check file types
        for file in files:
            if file.content_type not in self.allowed_types:
                raise HTTPException(
                    status_code=400, detail=f"File {file.filename} must be JPEG or PNG"
                )

            # Check file size
            content = await file.read()
            if len(content) > self.max_size:
                raise HTTPException(
                    status_code=400, detail=f"File {file.filename} exceeds 10MB limit"
                )

            # Reset file cursor for saving
            await file.seek(0)

    async def save_files(self, files: List[UploadFile]) -> List[str]:
        """
        Save uploaded files to local storage with unique filenames.
        
        Args:
            files: List of validated uploaded files
            
        Returns:
            List of file paths where images were saved
        """

        saved_paths = []

        for file in files:
            # Generate unique filename
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)

            # Save file
            async with aiofiles.open(file_path, "wb") as f:
                content = await file.read()
                await f.write(content)

            # Return path for API response
            saved_paths.append(file_path)

        return saved_paths


# Create service instance
photo_service = PhotoService()
