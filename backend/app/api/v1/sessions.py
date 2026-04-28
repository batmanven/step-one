from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from pathlib import Path
import json
from datetime import datetime

router = APIRouter(tags=["sessions"])


@router.get("/")
@router.get("")
async def list_sessions():
    """List all sessions from file-based storage"""
    sessions = []
    outputs_dir = Path(__file__).parent.parent.parent.parent / "outputs"

    # Look for all session status files
    status_files = list(outputs_dir.glob("*_status.json"))

    for status_file in status_files:
        try:
            with open(status_file, 'r') as f:
                data = json.load(f)
                session_id = data.get("session_id", status_file.stem.replace("_status", ""))
                sessions.append({
                    "_id": session_id,
                    "session_id": session_id,
                    "status": data.get("status", "unknown"),
                    "progress": data.get("progress", 0),
                    "stage": data.get("stage", "unknown"),
                    "created_at": datetime.fromtimestamp(status_file.stat().st_mtime).isoformat(),
                    "total_assets": len(data.get("outputs", {})),
                    "event_name": data.get("dataset_name", session_id.replace("session_", "event_"))
                })
        except Exception as e:
            print(f"Error reading {status_file.name}: {e}")

    # Sort by creation time (newest first)
    sessions.sort(key=lambda x: x["created_at"], reverse=True)

    return {"sessions": sessions}


@router.get("/text-content")
async def get_text_content(path: str):
    """Securely fetch the text content of a generated asset."""
    try:
        outputs_dir = Path(__file__).parent.parent.parent.parent / "outputs"
        # Sanitize path to prevent directory traversal
        filename = path.split("/")[-1]
        category = path.split("/")[-2] if "/" in path else ""
        
        target_path = outputs_dir / category / filename
        
        if not target_path.exists():
            # Try without category
            target_path = outputs_dir / filename
            
        if not target_path.exists() or not target_path.is_file():
            raise HTTPException(status_code=404, detail="File not found")
            
        with open(target_path, "r") as f:
            return {"content": f.read()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/{session_id}")
async def get_session(session_id: str):
    """Get session details by ID"""
    outputs_dir = Path(__file__).parent.parent.parent.parent / "outputs"
    status_file = outputs_dir / f"{session_id}_status.json"

    if not status_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")

    with open(status_file, 'r') as f:
        data = json.load(f)

    return {
        "_id": session_id,
        "session_id": session_id,
        **data,
        "created_at": datetime.fromtimestamp(status_file.stat().st_mtime).isoformat()
    }


@router.get("/{session_id}/outputs")
async def get_session_outputs(session_id: str):
    """Get all outputs for a session"""
    outputs = []
    outputs_dir = Path(__file__).parent.parent.parent.parent / "outputs"

    # Get collages
    linkedin_dir = outputs_dir / "linkedin"
    for collage in linkedin_dir.glob(f"{session_id}_*.jpg"):
        outputs.append({
            "id": f"{session_id}_collage",
            "type": "collage",
            "title": "LinkedIn Collage",
            "session_id": session_id,
            "url": f"/outputs/linkedin/{collage.name}",
            "created_at": datetime.fromtimestamp(collage.stat().st_mtime).isoformat()
        })

    # Get stories
    stories_dir = outputs_dir / "stories"
    for story in stories_dir.glob(f"{session_id}_story_*.jpg"):
        outputs.append({
            "id": story.stem,
            "type": "story",
            "title": f"Story {story.stem.split('_')[-1]}",
            "session_id": session_id,
            "url": f"/outputs/stories/{story.name}",
            "created_at": datetime.fromtimestamp(story.stat().st_mtime).isoformat()
        })

    # Get case studies
    case_studies_dir = outputs_dir / "case_studies"
    for case_study in case_studies_dir.glob(f"{session_id}_*.txt"):
        outputs.append({
            "id": case_study.stem,
            "type": "case_study",
            "title": "Case Study",
            "session_id": session_id,
            "url": f"/outputs/case_studies/{case_study.name}",
            "created_at": datetime.fromtimestamp(case_study.stat().st_mtime).isoformat()
        })
        
    # Get reels
    reels_dir = outputs_dir / "reels"
    if reels_dir.exists():
        for reel in reels_dir.glob(f"{session_id}_*.mp4"):
            outputs.append({
                "id": reel.stem,
                "type": "reel",
                "title": "Instagram Reel",
                "session_id": session_id,
                "url": f"/outputs/reels/{reel.name}",
                "created_at": datetime.fromtimestamp(reel.stat().st_mtime).isoformat()
            })

from fastapi.responses import FileResponse
import shutil
import tempfile

@router.get("/{session_id}/download-all")
async def download_all_session_assets(session_id: str):
    """Bundle all assets for a session into a zip file for download."""
    outputs_dir = Path(__file__).parent.parent.parent.parent / "outputs"
    
    # Create a temporary directory to gather files
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)
        session_export_dir = tmp_path / f"export_{session_id}"
        session_export_dir.mkdir()
        
        # Find all assets for this session
        found_any = False
        
        # Scan all subdirectories in outputs
        for category in ["linkedin", "instagram", "stories", "case_studies", "reels"]:
            cat_dir = outputs_dir / category
            if cat_dir.exists():
                for asset in cat_dir.glob(f"{session_id}_*"):
                    shutil.copy2(asset, session_export_dir / asset.name)
                    found_any = True
        
        if not found_any:
            raise HTTPException(status_code=404, detail="No assets found for this session")
            
        # Create zip
        zip_path = tmp_path / f"{session_id}_assets"
        shutil.make_archive(str(zip_path), 'zip', session_export_dir)
        
        return FileResponse(
            path=f"{zip_path}.zip",
            filename=f"{session_id}_content_bundle.zip",
            media_type="application/x-zip-compressed"
        )

