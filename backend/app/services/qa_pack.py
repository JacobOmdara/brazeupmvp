import os
import zipfile
import tempfile
import shutil
from pathlib import Path
from fastapi import HTTPException


class QAPackService:
    """
    A service class for bundling QA analysis artifacts into downloadable ZIP files.
    
    This class handles the creation of ZIP packages containing original images,
    segmentation masks, geometry data, analysis summaries, and job tickets.
    """
    
    def __init__(self):
        """
        Initialize the QAPackService with default file paths and configuration.
        
        Attributes:
            images_dir (Path): Path to the directory containing original images
            masks_dir (Path): Path to the directory containing segmentation masks  
            geometry_csv (Path): Path to the geometry.csv file
            summary_json (Path): Path to the summary.json file
            job_ticket_pdf (Path): Path to the job_ticket.pdf file
            qa_packs_dir (Path): Directory where generated ZIP files will be stored
            max_zip_size (int): Maximum allowed ZIP file size in bytes (50 MB)
        """
        self.images_dir = Path(r"C:\Users\talha\OneDrive\Desktop\Riippen\brazeupmvp\backend\app\tests\qa_test\images")
        self.masks_dir = Path(r"C:\Users\talha\OneDrive\Desktop\Riippen\brazeupmvp\backend\app\tests\qa_test\segmentation_masks") 
        self.geometry_csv = Path(r"C:\Users\talha\OneDrive\Desktop\Riippen\brazeupmvp\backend\app\tests\qa_test\geometry.csv")
        self.summary_json = Path(r"C:\Users\talha\OneDrive\Desktop\Riippen\brazeupmvp\backend\app\tests\qa_test\summary.json")
        self.job_ticket_pdf = Path(r"C:\Users\talha\OneDrive\Desktop\Riippen\brazeupmvp\backend\app\tests\qa_test\job_ticket.pdf")
        self.qa_packs_dir = Path(r"C:\Users\talha\OneDrive\Desktop\Riippen\brazeupmvp\backend\app\tests\qa_test\qa_packs")
        self.max_zip_size = 50 * 1024 * 1024  # 50 MB

    def validate_paths(self) -> bool:
        """
        Validate that all required files and directories exist.
        
        Returns:
            bool: True if all paths exist, otherwise raises HTTPException
            
        Raises:
            HTTPException: 400 error if any required path is missing
        """
        paths = [
            (self.images_dir, "images directory"),
            (self.masks_dir, "segmentation masks directory"),
            (self.geometry_csv, "geometry.csv"),
            (self.summary_json, "summary.json"), 
            (self.job_ticket_pdf, "job_ticket.pdf")
        ]
        
        for path, name in paths:
            if not path.exists():
                raise HTTPException(400, f"Missing: {name} at {path}")
        return True

    def create_qa_pack(self) -> str:
        """
        Create a ZIP file containing all QA analysis artifacts.
        
        This method bundles the original images, segmentation masks, geometry CSV,
        summary JSON, and job ticket PDF into a single downloadable ZIP file.
        
        Returns:
            str: Download URL for the created ZIP file
            
        Raises:
            HTTPException: 400 error if ZIP file exceeds size limit
            HTTPException: 500 error if ZIP creation fails
        """
        self.validate_paths()
        
        # Create temp directory for assembly
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Copy all files to temp directory
            shutil.copytree(self.images_dir, temp_path / "images")
            shutil.copytree(self.masks_dir, temp_path / "segmentation_masks")
            shutil.copy2(self.geometry_csv, temp_path / "geometry.csv")
            shutil.copy2(self.summary_json, temp_path / "summary.json") 
            shutil.copy2(self.job_ticket_pdf, temp_path / "job_ticket.pdf")
            
            # Create ZIP file
            self.qa_packs_dir.mkdir(exist_ok=True)
            zip_path = self.qa_packs_dir / "qa_pack.zip"
            
            with zipfile.ZipFile(zip_path, 'w') as zipf:
                for file in temp_path.rglob('*'):
                    if file.is_file():
                        zipf.write(file, file.relative_to(temp_path))
            
            # Validate ZIP file size
            if zip_path.stat().st_size > self.max_zip_size:
                zip_path.unlink()
                raise HTTPException(400, "ZIP file exceeds 50MB limit")
            
            # Return download URL
            return f"/qa-pack/download/{zip_path.name}"
        
qa_pack_service = QAPackService()