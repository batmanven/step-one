"""
Asset Selector: Evaluates and selects best images from dataset
based on aesthetic quality (OpenCV) and semantic relevance (YOLO, FER).
"""
import os
from pathlib import Path
from PIL import Image
import cv2
import numpy as np
from typing import List, Dict

try:
    from ultralytics import YOLO
    from fer.fer import FER
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False
    print("Warning: ML packages not available. Falling back to basic heuristics.")

class AssetSelector:
    def __init__(self, dataset_path: Path):
        self.dataset_path = dataset_path
        self.images_dir = dataset_path / "images"
        self.videos_dir = dataset_path / "videos"
        
        # Ensure directories exist
        self.images_dir.mkdir(parents=True, exist_ok=True)
        self.videos_dir.mkdir(parents=True, exist_ok=True)
        
        self.yolo_model = None
        self.fer_detector = None
        
        if ML_AVAILABLE:
            try:
                self.yolo_model = YOLO('yolov8n.pt')
                # Load FER for emotion detection
                self.fer_detector = FER(mtcnn=True)
            except Exception as e:
                print(f"Failed to load ML models: {e}")
    
    def select_assets(self, top_n: int = 20) -> List[Dict]:
        """Select top N images with a diversity factor for variety"""
        # Support multiple extensions and case sensitivity
        extensions = ["*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG", "*.webp", "*.WEBP"]
        images = []
        for ext in extensions:
            images.extend(list(self.images_dir.glob(ext)))
        
        # Remove duplicates
        images = list(set(images))
        
        if not images:
            print(f"No images found in {self.images_dir}")
            return []
        
        import random
        scored_assets = []
        for img_path in images:
            analysis = self._analyze_image(img_path)
            if analysis['score'] > 0:
                scored_assets.append({
                    "path": str(img_path),
                    "filename": img_path.name,
                    "score": analysis['score'],
                    "rationale": analysis['rationale'],
                    "metadata": analysis['metadata']
                })
        
        # Sort by score descending to see our quality distribution
        scored_assets.sort(key=lambda x: x["score"], reverse=True)
        
        # Filter for "Usable" images (score > 0.3) from the entire set of 100-200+ photos
        usable_pool = [a for a in scored_assets if float(a['score']) > 0.3]
        
        # If we don't have enough "good" photos, lower the bar slightly
        if len(usable_pool) < top_n:
            usable_pool = scored_assets[:top_n * 2]
            
        # Randomly sample from the ENTIRE usable pool (could be 100+ images)
        if len(usable_pool) > top_n:
            final_selection = random.sample(usable_pool, top_n)
            # Re-sort the final selection by score so the "best" of the batch are first
            final_selection.sort(key=lambda x: x["score"], reverse=True)
            return final_selection
        
        return scored_assets[:top_n]
    
    def _analyze_image(self, img_path: Path) -> Dict:
        """Run full AI analysis on an image"""
        try:
            img = cv2.imread(str(img_path))
            if img is None:
                return {"score": 0.0, "rationale": "Unreadable", "metadata": {}}
            
            # 1. Aesthetic Scoring (Sharpness & Composition)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            laplacian_var = cv2.Laplacian(gray, cv2.CV_64F).var()
            sharpness_score = min(laplacian_var / 800.0, 1.0) # Higher threshold for better quality
            
            # Penalize blurry images heavily
            if sharpness_score < 0.2:
                return {"score": 0.1, "rationale": "Image is too blurry", "metadata": {}}
                
            height, width = img.shape[:2]
            aspect_ratio = width / height
            orientation = "landscape" if aspect_ratio > 1 else "portrait" if aspect_ratio < 1 else "square"
            
            # 2. Semantic Scoring (YOLO)
            person_count = 0
            if self.yolo_model:
                results = self.yolo_model(img, verbose=False)[0]
                # Class 0 in COCO is 'person'
                persons = [box for box in results.boxes if int(box.cls) == 0]
                person_count = len(persons)
            
            # 3. Emotion Scoring (FER)
            positive_emotions = 0
            if self.fer_detector:
                emotions = self.fer_detector.detect_emotions(img)
                for face in emotions:
                    # Look for happy or surprise
                    if face['emotions']['happy'] > 0.5 or face['emotions']['surprise'] > 0.5:
                        positive_emotions += 1
            
            # Calculate composite score
            # Base aesthetic is important
            semantic_score = 0.0
            rationale_points = []
            
            if person_count > 0:
                # Reward 1-4 people (focus) or >10 people (crowd energy)
                if 1 <= person_count <= 4:
                    semantic_score += 0.4
                    rationale_points.append(f"Clear focus on {person_count} subjects.")
                elif person_count > 10:
                    semantic_score += 0.5
                    rationale_points.append(f"High crowd energy ({person_count} people detected).")
                else:
                    semantic_score += 0.2
            
            if positive_emotions > 0:
                semantic_score += 0.5 # Big boost for smiling/engaged faces
                rationale_points.append(f"Detected {positive_emotions} highly engaged/smiling faces.")
                
            # Combine
            final_score = (sharpness_score * 0.4) + (min(semantic_score, 1.0) * 0.6)
            final_score = round(final_score, 3)
            
            if not rationale_points:
                if sharpness_score > 0.7:
                    rationale_points.append("Good technical quality but low semantic action.")
                else:
                    rationale_points.append("Average quality, no strong semantic markers.")
                    
            metadata = {
                "sharpness": round(sharpness_score, 2),
                "people_count": person_count,
                "engaged_faces": positive_emotions,
                "orientation": orientation
            }
            
            return {
                "score": final_score,
                "rationale": " ".join(rationale_points),
                "metadata": metadata
            }
            
        except Exception as e:
            print(f"Error processing {img_path}: {e}")
            return {"score": 0.0, "rationale": "Error processing", "metadata": {}}
