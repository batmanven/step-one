from celery import Celery
from app.config import settings
from app.services.mongo_service import MongoDB, COLLECTION_ASSETS, COLLECTION_LOGS
from app.processors.metadata_extractor import MetadataExtractor
from app.processors.normalizer import MediaNormalizer
from app.processors.yolo_detector import yolo_detector
from app.services.s3_service import s3_service
from app.models.processing_log import ProcessingStage, LogStatus
from bson import ObjectId
import tempfile
import os

# Initialize Celery
celery_app = Celery(
    "stepone_tasks",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)


@celery_app.task(bind=True)
def extract_metadata_task(self, asset_id: str):
    """Extract metadata from an asset"""
    import time
    start_time = time.time()
    
    try:
        db = MongoDB.get_database()
        
        # Get asset from database
        asset = db[COLLECTION_ASSETS].find_one({"_id": ObjectId(asset_id)})
        if not asset:
            raise Exception(f"Asset {asset_id} not found")
        
        # Log start
        log_data = {
            "session_id": asset["session_id"],
            "asset_id": asset_id,
            "stage": ProcessingStage.INGESTION,
            "status": LogStatus.STARTED,
            "timestamp": time.time()
        }
        db[COLLECTION_LOGS].insert_one(log_data)
        
        # Download file from S3 to temp location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
        
        try:
            # Extract metadata
            metadata = MetadataExtractor.extract_from_s3(
                asset["s3_key"],
                s3_service,
                temp_path
            )
            
            # Update asset with metadata
            update_data = {
                "dimensions": metadata.get("dimensions", {"width": 0, "height": 0}),
                "orientation": metadata.get("orientation", "landscape"),
                "metadata": metadata
            }
            
            if "duration_seconds" in metadata:
                update_data["duration_seconds"] = metadata["duration_seconds"]
            
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
                    "stage": ProcessingStage.INGESTION,
                    "status": LogStatus.STARTED
                },
                {
                    "$set": {
                        "status": LogStatus.COMPLETED,
                        "duration_ms": duration_ms
                    }
                }
            )
            
            return {"status": "success", "asset_id": asset_id, "metadata": metadata}
            
        finally:
            # Clean up temp file
            if os.path.exists(temp_path):
                os.unlink(temp_path)
                
    except Exception as e:
        # Log failure
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "asset_id": asset_id,
                "stage": ProcessingStage.INGESTION,
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
def process_session_metadata(self, session_id: str):
    """Extract metadata for all assets in a session"""
    try:
        db = MongoDB.get_database()
        
        # Get all assets for session
        assets = db[COLLECTION_ASSETS].find({"session_id": session_id}).to_list(length=None)
        
        # Queue metadata extraction for each asset
        for asset in assets:
            extract_metadata_task.delay(str(asset["_id"]))
        
        return {"status": "queued", "session_id": session_id, "asset_count": len(assets)}
        
    except Exception as e:
        raise Exception(f"Failed to queue metadata extraction: {str(e)}")


@celery_app.task(bind=True)
def normalize_media_task(self, asset_id: str):
    """Normalize media file (transcode video, convert image to sRGB)"""
    import time
    start_time = time.time()
    
    try:
        db = MongoDB.get_database()
        
        # Get asset from database
        asset = db[COLLECTION_ASSETS].find_one({"_id": ObjectId(asset_id)})
        if not asset:
            raise Exception(f"Asset {asset_id} not found")
        
        # Log start
        log_data = {
            "session_id": asset["session_id"],
            "asset_id": asset_id,
            "stage": ProcessingStage.NORMALIZATION,
            "status": LogStatus.STARTED,
            "timestamp": time.time()
        }
        db[COLLECTION_LOGS].insert_one(log_data)
        
        # Download file from S3 to temp location
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            input_path = temp_file.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='_normalized') as temp_file:
            output_path = temp_file.name
        
        try:
            # Download file
            s3_service.s3_client.download_file(
                s3_service.bucket,
                asset["s3_key"],
                input_path
            )
            
            # Normalize based on file type
            file_ext = os.path.splitext(input_path)[1].lower()
            success = False
            
            if file_ext in ['.jpg', '.jpeg', '.png', '.webp', '.heic', '.heif']:
                success = MediaNormalizer.normalize_image(input_path, output_path)
            elif file_ext in ['.mp4', '.mov', '.avi', '.mkv']:
                success = MediaNormalizer.normalize_video(input_path, output_path)
            
            if success:
                # Upload normalized file to S3
                normalized_key = f"sessions/{asset['session_id']}/normalized/{os.path.basename(asset['s3_key'])}"
                s3_service.s3_client.upload_file(
                    output_path,
                    s3_service.bucket,
                    normalized_key,
                    ExtraArgs={'ContentType': asset.get('format', 'application/octet-stream')}
                )
                
                # Update asset with normalized file info
                db[COLLECTION_ASSETS].update_one(
                    {"_id": ObjectId(asset_id)},
                    {"$set": {"metadata.normalized_key": normalized_key}}
                )
            
            # Log completion
            duration_ms = int((time.time() - start_time) * 1000)
            db[COLLECTION_LOGS].update_one(
                {
                    "session_id": asset["session_id"],
                    "asset_id": asset_id,
                    "stage": ProcessingStage.NORMALIZATION,
                    "status": LogStatus.STARTED
                },
                {
                    "$set": {
                        "status": LogStatus.COMPLETED if success else LogStatus.FAILED,
                        "duration_ms": duration_ms
                    }
                }
            )
            
            return {"status": "success" if success else "failed", "asset_id": asset_id}
            
        finally:
            # Clean up temp files
            if os.path.exists(input_path):
                os.unlink(input_path)
            if os.path.exists(output_path):
                os.unlink(output_path)
                
    except Exception as e:
        # Log failure
        duration_ms = int((time.time() - start_time) * 1000)
        db[COLLECTION_LOGS].update_one(
            {
                "asset_id": asset_id,
                "stage": ProcessingStage.NORMALIZATION,
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
