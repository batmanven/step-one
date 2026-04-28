import os
import sys
from pathlib import Path
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List
import asyncio

router = APIRouter()

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

class ProcessRequest(BaseModel):
    dataset_name: str
    confidence_threshold: Optional[float] = 0.80

class ProcessResponse(BaseModel):
    session_id: str
    status: str
    message: str
    dataset_path: str

@router.post("/{dataset_name}", response_model=ProcessResponse)
async def process_dataset(dataset_name: str, background_tasks: BackgroundTasks):
    """Process an event dataset and generate all outputs"""

    # Validate dataset exists
    dataset_path = Path(f"/Users/priyanshnarang/Desktop/stepone-ai/event_datasets/{dataset_name}")
    if not dataset_path.exists():
        raise HTTPException(status_code=404, detail=f"Dataset {dataset_name} not found")

    images_dir = dataset_path / "images"
    if not images_dir.exists() or len(list(images_dir.glob("*"))) == 0:
        raise HTTPException(status_code=400, detail="No images found in dataset")

    session_id = f"session_{len(list(Path('outputs').glob('*'))) + 1}"

    # Start background processing
    background_tasks.add_task(run_processing, dataset_name, session_id, dataset_path)

    return ProcessResponse(
        session_id=session_id,
        status="processing",
        message=f"Started processing {dataset_name}",
        dataset_path=str(dataset_path)
    )

@router.get("/{session_id}/status")
async def get_processing_status(session_id: str):
    """Get processing status for a session"""
    status_file = Path(f"outputs/{session_id}_status.json")
    if not status_file.exists():
        raise HTTPException(status_code=404, detail="Session not found")
    
    import json
    with open(status_file, 'r') as f:
        return json.load(f)

async def run_processing(dataset_name: str, session_id: str, dataset_path: Path):
    """Background task to process dataset"""
    from app.processors.asset_selector import AssetSelector
    from app.processors.copy_generator import CopyGenerator
    from app.processors.collage_generator import CollageGenerator
    from app.processors.story_generator import StoryGenerator
    from app.processors.case_study_generator import CaseStudyGenerator
    from app.processors.video_generator import VideoGenerator
    import json
    
    status = {
        "session_id": session_id,
        "status": "processing",
        "stage": "initializing",
        "progress": 0,
        "outputs": {}
    }
    
    status_file = Path(f"outputs/{session_id}_status.json")
    with open(status_file, 'w') as f:
        json.dump(status, f)
    
    try:
        # Stage 1: Asset Selection
        status["stage"] = "asset_selection"
        status["progress"] = 10
        with open(status_file, 'w') as f:
            json.dump(status, f)
        
        selector = AssetSelector(dataset_path)
        selected_assets = selector.select_assets()
        
        # Stage 2: Copy Generation
        status["stage"] = "copy_generation"
        status["progress"] = 30
        with open(status_file, 'w') as f:
            json.dump(status, f)
        
        copy_gen = CopyGenerator()
        copies = copy_gen.generate_all(selected_assets, dataset_name)
        
        # Stage 3: Collage Generation
        status["stage"] = "collage_generation"
        status["progress"] = 50
        with open(status_file, 'w') as f:
            json.dump(status, f)
        
        collage_gen = CollageGenerator()
        collage_path = collage_gen.create_linkedin_collage(selected_assets[:6], session_id)
        
        # Stage 4: Story Generation
        status["stage"] = "story_generation"
        status["progress"] = 70
        with open(status_file, 'w') as f:
            json.dump(status, f)
        
        story_gen = StoryGenerator()
        stories_json = copies.get("stories_json", None)
        stories = story_gen.create_stories(selected_assets[:4], session_id, stories_json)
        
        # Stage 5: Video Reel Generation
        status["stage"] = "video_generation"
        status["progress"] = 80
        with open(status_file, 'w') as f:
            json.dump(status, f)
            
        video_gen = VideoGenerator(dataset_path)
        reel_path = video_gen.create_highlight_reel(session_id, target_duration=30)
        
        # Stage 6: Case Study
        status["stage"] = "case_study"
        status["progress"] = 90
        with open(status_file, 'w') as f:
            json.dump(status, f)
        
        case_study_gen = CaseStudyGenerator()
        case_study_path = case_study_gen.generate(selected_assets, copies, dataset_name, session_id)
        
        # Complete
        status["status"] = "completed"
        status["progress"] = 100
        status["outputs"] = {
            "linkedin_collage": str(collage_path) if collage_path else None,
            "linkedin_caption": copies.get("linkedin", ""),
            "instagram_caption": copies.get("instagram", ""),
            "stories": [str(s) for s in stories] if stories else [],
            "video_reel": str(reel_path) if reel_path else None,
            "case_study": str(case_study_path) if case_study_path else None
        }
        with open(status_file, 'w') as f:
            json.dump(status, f)
        
    except Exception as e:
        status["status"] = "failed"
        status["error"] = str(e)
        with open(status_file, 'w') as f:
            json.dump(status, f)
        raise
