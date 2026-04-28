"""
Collage Generator: Creates LinkedIn post collages from selected images.
Uses Saliency-Aware cropping (Face Detection) to preserve subjects.
"""
from PIL import Image
from pathlib import Path
from typing import List, Dict
import cv2
import numpy as np

class CollageGenerator:
    def __init__(self):
        # Load Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

    def create_linkedin_collage(self, assets: List[Dict], session_id: str) -> Path:
        """Create a 4-6 image collage for LinkedIn"""
        selected = assets[:6]
        num_images = len(selected)
        
        if num_images == 0:
            raise ValueError("No assets provided")
        
        if num_images <= 2:
            cols, rows = num_images, 1
        elif num_images <= 4:
            cols, rows = 2, 2
        else:
            cols, rows = 3, 2
        
        canvas_width = 1200
        canvas_height = 1200
        padding = 10
        
        cell_width = (canvas_width - (cols + 1) * padding) // cols
        cell_height = (canvas_height - (rows + 1) * padding) // rows
        
        collage = Image.new('RGB', (canvas_width, canvas_height), (255, 255, 255))
        
        for idx, asset in enumerate(selected):
            img_path = asset["path"]
            try:
                img = Image.open(img_path)
                img = self._resize_and_crop(img, cell_width, cell_height, img_path)
                
                col = idx % cols
                row = idx // cols
                x = padding + col * (cell_width + padding) + (cell_width - img.width) // 2
                y = padding + row * (cell_height + padding) + (cell_height - img.height) // 2
                
                collage.paste(img, (x, y))
            
            except Exception as e:
                print(f"Error processing {img_path}: {e}")
                continue
        
        output_dir = Path("outputs/linkedin")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{session_id}_collage.jpg"
        collage.save(output_path, "JPEG", quality=95)
        
        return output_path
    
    def _get_salient_center(self, img_path: str, width: int, height: int) -> tuple:
        """Use OpenCV face detection to find the center of attention"""
        try:
            cv_img = cv2.imread(img_path)
            if cv_img is None:
                return width // 2, height // 2
                
            gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
            
            if len(faces) == 0:
                return width // 2, height // 2
                
            # Calculate bounding box of all faces
            x_min = min([f[0] for f in faces])
            y_min = min([f[1] for f in faces])
            x_max = max([f[0] + f[2] for f in faces])
            y_max = max([f[1] + f[3] for f in faces])
            
            center_x = (x_min + x_max) // 2
            center_y = (y_min + y_max) // 2
            
            return center_x, center_y
        except Exception as e:
            print(f"Saliency detection failed for {img_path}: {e}")
            return width // 2, height // 2

    def _resize_and_crop(self, img: Image, target_width: int, target_height: int, img_path: str) -> Image:
        """Resize and crop image using saliency center"""
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height
        
        # Get face center before resizing
        center_x, center_y = self._get_salient_center(img_path, img.width, img.height)
        
        if img_ratio > target_ratio:
            # Image is wider, scale height to match target, crop width
            new_height = target_height
            new_width = int(target_height * img_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Scale center
            center_x = int(center_x * (new_height / img.height))
            
            # Calculate crop boundaries
            left = max(0, min(center_x - target_width // 2, new_width - target_width))
            img = img.crop((left, 0, left + target_width, target_height))
        else:
            # Image is taller, scale width to match target, crop height
            new_width = target_width
            new_height = int(target_width / img_ratio)
            img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            
            # Scale center
            center_y = int(center_y * (new_width / img.width))
            
            # Calculate crop boundaries
            top = max(0, min(center_y - target_height // 2, new_height - target_height))
            img = img.crop((0, top, target_width, top + target_height))
            
        return img
