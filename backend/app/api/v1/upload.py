from fastapi import APIRouter, HTTPException, UploadFile, File
from typing import List
import uuid
import os
import zipfile
import shutil
from pathlib import Path

router = APIRouter(prefix="/upload", tags=["upload"])

# Allowed file types
ALLOWED_IMAGE_TYPES = {
    ".jpg", ".jpeg", ".png", ".webp", ".heic"
}
ALLOWED_VIDEO_TYPES = {
    ".mp4", ".mov", ".avi", ".mkv"
}

@router.post("/bulk-zip")
async def upload_bulk_zip(
    event_name: str,
    file: UploadFile = File(...)
):
    """Upload a ZIP file, extract it, and organize into event_datasets/"""
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded or filename is missing")
        
    if not file.filename.endswith(".zip"):
        raise HTTPException(status_code=400, detail="Only .zip files are allowed")

    # Create dataset directory
    clean_name = event_name.lower().replace(" ", "_")
    dataset_dir = Path("event_datasets") / clean_name
    images_dir = dataset_dir / "images"
    video_dir = dataset_dir / "video"

    # Ensure clean start
    if dataset_dir.exists():
        shutil.rmtree(dataset_dir)
    
    images_dir.mkdir(parents=True)
    video_dir.mkdir(parents=True)

    # Save temp zip
    temp_zip = Path(f"temp_{uuid.uuid4()}.zip")
    try:
        with open(temp_zip, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Extract
        with zipfile.ZipFile(temp_zip, 'r') as zip_ref:
            for member in zip_ref.infolist():
                if member.is_dir():
                    continue
                
                filename = os.path.basename(member.filename)
                if not filename or filename.startswith('.'): 
                    continue # Skip hidden files
                
                # Sniff file type
                ext = os.path.splitext(filename)[1].lower()
                is_image = ext in ALLOWED_IMAGE_TYPES
                is_video = ext in ALLOWED_VIDEO_TYPES

                target_dir = images_dir if is_image else video_dir if is_video else None
                
                if target_dir:
                    source = zip_ref.open(member)
                    target_path = target_dir / filename
                    with open(target_path, "wb") as target_file:
                        shutil.copyfileobj(source, target_file)
                    source.close()

    except Exception as e:
        if dataset_dir.exists():
            shutil.rmtree(dataset_dir)
        raise HTTPException(status_code=500, detail=f"Extraction failed: {str(e)}")
    finally:
        if temp_zip.exists():
            os.remove(temp_zip)

    return {
        "status": "success",
        "dataset_name": clean_name,
        "message": f"Dataset {clean_name} created and organized with {len(list(images_dir.glob('*')))} images and {len(list(video_dir.glob('*')))} videos."
    }
