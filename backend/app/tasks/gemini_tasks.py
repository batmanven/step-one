from celery import Celery
from app.config import settings
from app.services.mongo_service import MongoDB, COLLECTION_ASSETS, COLLECTION_LOGS, COLLECTION_SESSIONS, COLLECTION_OUTPUTS
from app.services.gemini_service import gemini_service
from app.models.output import Output, OutputType, OutputStatus, OutputContent
from app.models.processing_log import ProcessingStage, LogStatus
from bson import ObjectId
import time

# Initialize Celery
celery_app = Celery(
    "stepone_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


@celery_app.task(bind=True)
def generate_linkedin_content_task(self, session_id: str):
    """Generate LinkedIn post content using Gemini"""
    start_time = time.time()
    
    try:
        db = MongoDB.get_database()
        
        # Get session
        session = db[COLLECTION_SESSIONS].find_one({"_id": ObjectId(session_id)})
        if not session:
            raise Exception(f"Session {session_id} not found")
        
        # Log start
        log_data = {
            "session_id": session_id,
            "stage": ProcessingStage.TRANSFORMATION,
            "status": LogStatus.STARTED,
            "timestamp": time.time()
        }
        db[COLLECTION_LOGS].insert_one(log_data)
        
        # Get selected assets (hero and action)
        selected_assets = list(db[COLLECTION_ASSETS].find({
            "session_id": session_id,
            "analysis.category": {"$in": ["hero", "action"]}
        }).limit(6))
        
        # Get analysis data
        analysis_data = session.get("metadata", {})
        
        # Generate caption
        caption = gemini_service.generate_linkedin_caption(
            session["event_name"],
            selected_assets,
            analysis_data
        )
        
        # Create output record
        output_data = {
            "session_id": session_id,
            "output_type": OutputType.LINKEDIN,
            "status": OutputStatus.COMPLETED,
            "confidence_score": 0.85,
            "flagged": False,
            "content": {
                "linkedin": {
                    "collage_url": "",  # Will be filled after collage generation
                    "caption": caption,
                    "selected_asset_ids": [str(a["_id"]) for a in selected_assets]
                }
            }
        }
        
        result = db[COLLECTION_OUTPUTS].insert_one(output_data)
        
        # Log completion
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "session_id": session_id,
                "stage": ProcessingStage.TRANSFORMATION,
                "status": LogStatus.STARTED
            },
            {
                "$set": {
                    "status": LogStatus.COMPLETED,
                    "duration_ms": duration_ms
                }
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "output_id": str(result.inserted_id),
            "caption": caption
        }
        
    except Exception as e:
        # Log failure
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "session_id": session_id,
                "stage": ProcessingStage.TRANSFORMATION,
                "status": LogStatus.STARTED
            },
            {
                "$set": {
                    "status": LogStatus.FAILED,
                    "duration_ms": duration_ms,
                    "error_message": str(e)
                }
            }
        )
        raise


@celery_app.task(bind=True)
def generate_instagram_content_task(self, session_id: str):
    """Generate Instagram reel and stories content using Gemini"""
    start_time = time.time()
    
    try:
        db = MongoDB.get_database()
        
        # Get session
        session = db[COLLECTION_SESSIONS].find_one({"_id": ObjectId(session_id)})
        if not session:
            raise Exception(f"Session {session_id} not found")
        
        # Log start
        log_data = {
            "session_id": session_id,
            "stage": ProcessingStage.TRANSFORMATION,
            "status": LogStatus.STARTED,
            "timestamp": time.time()
        }
        db[COLLECTION_LOGS].insert_one(log_data)
        
        # Get selected assets
        selected_assets = list(db[COLLECTION_ASSETS].find({
            "session_id": session_id,
            "analysis.category": {"$in": ["hero", "action"]}
        }))
        
        # Get analysis data
        analysis_data = session.get("metadata", {})
        
        # Generate Instagram caption
        caption = gemini_service.generate_instagram_caption(
            session["event_name"],
            selected_assets,
            analysis_data
        )
        
        # Create output record for reel
        reel_output = {
            "session_id": session_id,
            "output_type": OutputType.INSTAGRAM_REEL,
            "status": OutputStatus.COMPLETED,
            "confidence_score": 0.85,
            "flagged": False,
            "content": {
                "instagram_reel": {
                    "video_url": "",  # Will be filled after reel generation
                    "caption": caption,
                    "duration_seconds": 30.0,
                    "selected_asset_ids": [str(a["_id"]) for a in selected_assets[:10]]
                }
            }
        }
        
        db[COLLECTION_OUTPUTS].insert_one(reel_output)
        
        # Generate stories text overlays
        story_assets = selected_assets[:4]
        frames = []
        for i, asset in enumerate(story_assets):
            text = gemini_service.generate_story_text(
                session["event_name"],
                i,
                len(story_assets),
                asset
            )
            frames.append({
                "image_url": asset.get("s3_url", ""),
                "text_overlay": text,
                "sequence_order": i,
                "selected_asset_id": str(asset["_id"])
            })
        
        # Create output record for stories
        stories_output = {
            "session_id": session_id,
            "output_type": OutputType.INSTAGRAM_STORIES,
            "status": OutputStatus.COMPLETED,
            "confidence_score": 0.85,
            "flagged": False,
            "content": {
                "instagram_stories": {
                    "frames": frames
                }
            }
        }
        
        db[COLLECTION_OUTPUTS].insert_one(stories_output)
        
        # Log completion
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "session_id": session_id,
                "stage": ProcessingStage.TRANSFORMATION,
                "status": LogStatus.STARTED
            },
            {
                "$set": {
                    "status": LogStatus.COMPLETED,
                    "duration_ms": duration_ms
                }
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "caption": caption,
            "stories_count": len(frames)
        }
        
    except Exception as e:
        # Log failure
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "session_id": session_id,
                "stage": ProcessingStage.TRANSFORMATION,
                "status": LogStatus.STARTED
            },
            {
                "$set": {
                    "status": LogStatus.FAILED,
                    "duration_ms": duration_ms,
                    "error_message": str(e)
                }
            }
        )
        raise


@celery_app.task(bind=True)
def generate_case_study_task(self, session_id: str):
    """Generate case study draft using Gemini"""
    start_time = time.time()
    
    try:
        db = MongoDB.get_database()
        
        # Get session
        session = db[COLLECTION_SESSIONS].find_one({"_id": ObjectId(session_id)})
        if not session:
            raise Exception(f"Session {session_id} not found")
        
        # Log start
        log_data = {
            "session_id": session_id,
            "stage": ProcessingStage.TRANSFORMATION,
            "status": LogStatus.STARTED,
            "timestamp": time.time()
        }
        db[COLLECTION_LOGS].insert_one(log_data)
        
        # Get selected assets
        selected_assets = list(db[COLLECTION_ASSETS].find({
            "session_id": session_id,
            "analysis.category": {"$in": ["hero", "action"]}
        }))
        
        # Get analysis data
        analysis_data = session.get("metadata", {})
        
        # Generate case study
        case_study = gemini_service.generate_case_study(
            session["event_name"],
            selected_assets,
            analysis_data
        )
        
        # Create output record
        output_data = {
            "session_id": session_id,
            "output_type": OutputType.CASE_STUDY,
            "status": OutputStatus.COMPLETED,
            "confidence_score": 0.85,
            "flagged": False,
            "content": {
                "case_study": {
                    "executive_summary": case_study.get("executive_summary", ""),
                    "engagement_summary": case_study.get("engagement_summary", ""),
                    "sponsor_visibility": case_study.get("sponsor_visibility", ""),
                    "key_moments": case_study.get("key_moments", []),
                    "selected_asset_ids": [str(a["_id"]) for a in selected_assets]
                }
            }
        }
        
        result = db[COLLECTION_OUTPUTS].insert_one(output_data)
        
        # Log completion
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "session_id": session_id,
                "stage": ProcessingStage.TRANSFORMATION,
                "status": LogStatus.STARTED
            },
            {
                "$set": {
                    "status": LogStatus.COMPLETED,
                    "duration_ms": duration_ms
                }
            }
        )
        
        return {
            "status": "success",
            "session_id": session_id,
            "output_id": str(result.inserted_id),
            "case_study": case_study
        }
        
    except Exception as e:
        # Log failure
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "session_id": session_id,
                "stage": ProcessingStage.TRANSFORMATION,
                "status": LogStatus.STARTED
            },
            {
                "$set": {
                    "status": LogStatus.FAILED,
                    "duration_ms": duration_ms,
                    "error_message": str(e)
                }
            }
        )
        raise
