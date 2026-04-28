from celery import Celery
from app.config import settings
from app.services.mongo_service import MongoDB, COLLECTION_ASSETS, COLLECTION_LOGS
from app.processors.aesthetic_scorer import aesthetic_scorer
from app.services.s3_service import s3_service
from app.models.processing_log import ProcessingStage, LogStatus
from bson import ObjectId
import tempfile
import os
import time

# Initialize Celery
celery_app = Celery(
    "stepone_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)


@celery_app.task(bind=True)
def aesthetic_scoring_task(self, asset_id: str):
    """Run aesthetic scoring on an image asset"""
    start_time = time.time()
    
    try:
        db = MongoDB.get_database()
        
        # Get asset from database
        asset = db[COLLECTION_ASSETS].find_one({"_id": ObjectId(asset_id)})
        if not asset:
            raise Exception(f"Asset {asset_id} not found")
        
        # Only process images
        if asset.get("file_type") != "image":
            return {"status": "skipped", "reason": "not an image", "asset_id": asset_id}
        
        # Log start
        log_data = {
            "session_id": asset["session_id"],
            "asset_id": asset_id,
            "stage": ProcessingStage.ANALYSIS,
            "status": LogStatus.STARTED,
            "timestamp": time.time()
        }
        db[COLLECTION_LOGS].insert_one(log_data)
        
        # Download file from S3 to temp location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            input_path = temp_file.name
        
        try:
            # Download file
            s3_service.s3_client.download_file(
                s3_service.bucket,
                asset["s3_key"],
                input_path
            )
            
            # Run aesthetic scoring
            scores = aesthetic_scorer.get_detailed_scores(input_path)
            
            # Update asset with aesthetic scores
            update_data = {
                "analysis.aesthetic_score": scores["composite"],
                "analysis.composition_score": scores["composition"],
                "analysis.lighting_score": scores["lighting"],
                "analysis.color_harmony_score": scores["color_harmony"],
                "analysis.semantic_score": scores["semantic"]
            }
            
            db[COLLECTION_ASSETS].update_one(
                {"_id": ObjectId(asset_id)},
                {"$set": update_data}
            )
            
            # Log completion
            duration_ms = int((time.time() - start_time) * 1000)
            db[COLLECTION_LOGS].update_one(
                {
                    "session_id": asset["session_id"],
                    "asset_id": asset_id,
                    "stage": ProcessingStage.ANALYSIS,
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
                "asset_id": asset_id,
                "aesthetic_score": scores["composite"]
            }
            
        finally:
            # Clean up temp file
            if os.path.exists(input_path):
                os.unlink(input_path)
                
    except Exception as e:
        # Log failure
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "asset_id": asset_id,
                "stage": ProcessingStage.ANALYSIS,
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
