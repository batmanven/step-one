from celery import Celery
from app.config import settings
from app.services.mongo_service import MongoDB, COLLECTION_ASSETS, COLLECTION_LOGS, COLLECTION_SESSIONS
from app.processors.asset_selector import asset_selector
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
def selection_task(self, session_id: str):
    """Run asset selection and categorization for a session"""
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
            "stage": ProcessingStage.SELECTION,
            "status": LogStatus.STARTED,
            "timestamp": time.time()
        }
        db[COLLECTION_LOGS].insert_one(log_data)
        
        # Get all assets for session
        assets = list(db[COLLECTION_ASSETS].find({"session_id": session_id}))
        
        if not assets:
            return {"status": "skipped", "reason": "no assets", "session_id": session_id}
        
        # Convert to dict format for selector
        assets_dict = []
        for asset in assets:
            asset_dict = dict(asset)
            asset_dict["_id"] = str(asset["_id"])
            assets_dict.append(asset_dict)
        
        # Run selection
        confidence_threshold = session.get("confidence_threshold", 0.6)
        result = asset_selector.select_assets_for_session(assets_dict, confidence_threshold)
        
        # Update each asset with selection data
        for category in result["categorized_assets"].values():
            for asset in category:
                db[COLLECTION_ASSETS].update_one(
                    {"_id": ObjectId(asset["_id"])},
                    {"$set": {
                        "analysis.composite_score": asset["analysis"]["composite_score"],
                        "analysis.category": asset["analysis"]["category"],
                        "analysis.selection_rationale": asset["analysis"]["selection_rationale"]
                    }}
                )
        
        # Update session with selection statistics
        db[COLLECTION_SESSIONS].update_one(
            {"_id": ObjectId(session_id)},
            {"$set": {
                "metadata.selection_stats": result["statistics"],
                "processed_assets": result["statistics"]["selected_count"]
            }}
        )
        
        # Log completion
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "session_id": session_id,
                "stage": ProcessingStage.SELECTION,
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
            "statistics": result["statistics"]
        }
        
    except Exception as e:
        # Log failure
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "session_id": session_id,
                "stage": ProcessingStage.SELECTION,
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
