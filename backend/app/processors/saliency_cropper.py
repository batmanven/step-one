import cv2
import numpy as np
from PIL import Image
from typing import Tuple, Optional
import tempfile
import os


class SaliencyCropper:
    """Saliency-aware smart cropping for aspect ratio conversion"""
    
    def __init__(self):
        """Initialize saliency detector with safe attribute checking"""
        self.saliency = None
        # Only attempt if the module and attribute exist
        if hasattr(cv2, 'saliency') and hasattr(cv2.saliency, 'StaticSaliencySpectralResidual_create'):
            try:
                self.saliency = cv2.saliency.StaticSaliencySpectralResidual_create()
                print("Premium Saliency Detector Initialized")
            except Exception:
                print("Falling back to Gradient Saliency Mode")
        else:
            print("System: Using Native Gradient Saliency (Smart Heatmap Mode)")
    
    def generate_saliency_map(self, image_path: str) -> Optional[np.ndarray]:
        """Generate saliency map for an image with fallback for missing modules"""
        try:
            img = cv2.imread(image_path)
            if img is None:
                return None

            # Try using the specialized saliency module if available
            if self.saliency:
                try:
                    success, saliency_map = self.saliency.computeSaliency(img)
                    if success:
                        # Normalize to 0-255
                        return (saliency_map * 255).astype("uint8")
                except Exception as e:
                    print(f"Saliency computation failed, falling back: {e}")

            # Fallback: Gradient-based saliency (Edge density)
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            grad_x = cv2.Sobel(gray, cv2.CV_16S, 1, 0, ksize=3)
            grad_y = cv2.Sobel(gray, cv2.CV_16S, 0, 1, ksize=3)
            abs_grad_x = cv2.convertScaleAbs(grad_x)
            abs_grad_y = cv2.convertScaleAbs(grad_y)
            mag = cv2.addWeighted(abs_grad_x, 0.5, abs_grad_y, 0.5, 0)
            saliency_map = cv2.GaussianBlur(mag, (21, 21), 0)
            saliency_map = cv2.equalizeHist(saliency_map)
            return saliency_map
            
        except Exception as e:
            print(f"Error generating saliency map: {e}")
            return None
    
    def find_safe_crop_region(
        self,
        saliency_map: np.ndarray,
        target_width: int,
        target_height: int,
        original_width: int,
        original_height: int
    ) -> Tuple[int, int, int, int]:
        """
        Find optimal crop region based on saliency map
        
        Args:
            saliency_map: Saliency map
            target_width: Target crop width
            target_height: Target crop height
            original_width: Original image width
            original_height: Original image height
            
        Returns:
            Tuple: (x, y, width, height) of crop region
        """
        # Calculate maximum possible crop positions
        max_x = original_width - target_width
        max_y = original_height - target_height
        
        if max_x <= 0 or max_y <= 0:
            # Image is smaller than target, return full image
            return (0, 0, original_width, original_height)
        
        # Slide window to find region with highest saliency
        best_score = 0
        best_x, best_y = 0, 0
        
        # Sample positions (not every pixel for efficiency)
        step_x = max(1, max_x // 20)
        step_y = max(1, max_y // 20)
        
        for y in range(0, max_y + 1, step_y):
            for x in range(0, max_x + 1, step_x):
                # Extract region from saliency map
                region = saliency_map[y:y+target_height, x:x+target_width]
                
                # Calculate average saliency in region
                score = np.mean(region)
                
                if score > best_score:
                    best_score = score
                    best_x, best_y = x, y
        
        return (best_x, best_y, target_width, target_height)
    
    def smart_crop(
        self,
        image_path: str,
        target_aspect_ratio: str = "9:16",
        output_path: Optional[str] = None
    ) -> Optional[str]:
        """
        Smart crop image to target aspect ratio using saliency detection
        
        Args:
            image_path: Path to input image
            target_aspect_ratio: Target aspect ratio (e.g., "9:16", "1:1", "16:9")
            output_path: Path to save cropped image (if None, creates temp file)
            
        Returns:
            str: Path to cropped image or None
        """
        try:
            # Parse aspect ratio
            if target_aspect_ratio == "9:16":
                target_ratio = 9/16
            elif target_aspect_ratio == "1:1":
                target_ratio = 1.0
            elif target_aspect_ratio == "16:9":
                target_ratio = 16/9
            else:
                target_ratio = 9/16  # Default to vertical
            
            # Load image
            image = cv2.imread(image_path)
            if image is None:
                return None
            
            h, w = image.shape[:2]
            current_ratio = w / h
            
            # Generate saliency map
            saliency_map = self.generate_saliency_map(image_path)
            
            if saliency_map is None:
                # Fallback to center crop
                saliency_map = np.ones((h, w), dtype=np.uint8) * 128
            
            # Calculate target dimensions
            if current_ratio > target_ratio:
                # Image is wider than target - crop width
                target_height = h
                target_width = int(h * target_ratio)
            else:
                # Image is taller than target - crop height
                target_width = w
                target_height = int(w / target_ratio)
            
            # Find optimal crop region
            x, y, crop_w, crop_h = self.find_safe_crop_region(
                saliency_map,
                target_width,
                target_height,
                w,
                h
            )
            
            # Crop image
            cropped = image[y:y+crop_h, x:x+crop_w]
            
            # Save output
            if output_path is None:
                output_path = tempfile.mktemp(suffix='.jpg')
            
            cv2.imwrite(output_path, cropped)
            
            return output_path
            
        except Exception as e:
            print(f"Error in smart crop: {e}")
            return None
    
    def crop_to_square(self, image_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Smart crop to square (1:1) aspect ratio"""
        return self.smart_crop(image_path, "1:1", output_path)
    
    def crop_to_vertical(self, image_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Smart crop to vertical (9:16) aspect ratio for stories"""
        return self.smart_crop(image_path, "9:16", output_path)
    
    def crop_to_landscape(self, image_path: str, output_path: Optional[str] = None) -> Optional[str]:
        """Smart crop to landscape (16:9) aspect ratio"""
        return self.smart_crop(image_path, "16:9", output_path)
    
    def batch_crop_assets(
        self,
        assets: list,
        target_aspect_ratio: str = "9:16"
    ) -> list:
        """
        Batch crop multiple assets
        
        Args:
            assets: List of asset dictionaries with path
            target_aspect_ratio: Target aspect ratio
            
        Returns:
            list: Updated assets with cropped variant info
        """
        for asset in assets:
            try:
                input_path = asset["path"]
                
                # Smart crop
                output_dir = os.path.dirname(input_path)
                cropped_filename = f"cropped_{target_aspect_ratio.replace(':', '_')}_{os.path.basename(input_path)}"
                cropped_path = os.path.join(output_dir, cropped_filename)
                
                result_path = self.smart_crop(input_path, target_aspect_ratio, cropped_path)
                
                if result_path:
                    # Add to asset transformations
                    if "transformations" not in asset:
                        asset["transformations"] = {}
                    if "cropped_variants" not in asset["transformations"]:
                        asset["transformations"]["cropped_variants"] = []
                    
                    # Assume URL can be derived from path
                    asset_url = f"/outputs/{os.path.relpath(result_path, 'outputs')}"
                    
                    asset["transformations"]["cropped_variants"].append({
                        "aspect_ratio": target_aspect_ratio,
                        "path": result_path,
                        "url": asset_url
                    })
                    
            except Exception as e:
                print(f"Error cropping asset {asset.get('_id')}: {e}")
        
        return assets


# Singleton instance
saliency_cropper = SaliencyCropper()
