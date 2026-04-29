"""
Story Generator: Creates Instagram Stories (3-4 vertical frames)
Uses Saliency-Aware cropping (Face Detection) to preserve subjects.
"""

from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
from typing import List, Dict
import cv2
import numpy as np
import json


class StoryGenerator:
    def __init__(self):
        # Load Haar Cascade for face detection
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        )

    def create_stories(
        self, assets: List[Dict], session_id: str, stories_json: str = None
    ) -> List[Path]:
        """Create 3-4 Instagram Story frames with sequential narrative"""
        selected = assets[:4]
        stories = []

        narratives = []
        if stories_json:
            try:
                data = json.loads(stories_json)
                for item in data:
                    narratives.append(
                        (item.get("title", "Event"), item.get("subtitle", "Highlights"))
                    )
            except Exception as e:
                print(f"Failed to parse stories_json: {e}")

        if not narratives:
            narratives = [
                ("The Event Begins", "Excitement fills the room as attendees arrive"),
                ("Key Moments", "Engaging sessions and powerful presentations"),
                ("Networking", "Connecting with industry leaders and peers"),
                ("Memories Made", "Unforgettable moments captured forever"),
            ]

        output_dir = Path("outputs/stories")
        output_dir.mkdir(parents=True, exist_ok=True)

        for idx, asset in enumerate(selected):
            if idx >= len(narratives):
                break
            title, subtitle = narratives[idx]
            img_path = asset["path"]
            try:
                story_path = self._create_story_frame(
                    img_path, title, subtitle, idx + 1, session_id
                )
                stories.append(story_path)
            except Exception as e:
                print(f"Error creating story frame {idx}: {e}")
                continue

        return stories

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

    def _create_story_frame(
        self, img_path: str, title: str, subtitle: str, frame_num: int, session_id: str
    ) -> Path:
        """Create a single Instagram Story frame (9:16 aspect ratio)"""
        width = 1080
        height = 1920

        # Premium dark theme background
        canvas = Image.new("RGB", (width, height), (15, 15, 25))

        try:
            img = Image.open(img_path)

            # Calculate the target image area (top 75% of the story)
            img_height = int(height * 0.75)

            # CROP to the EXACT aspect ratio of the target box to avoid STRETCHING
            img = self._crop_to_portrait(img, width, img_height, img_path)

            # Resize to fill the box perfectly
            img = img.resize((width, img_height), Image.Resampling.LANCZOS)
            canvas.paste(img, (0, 0))

            # Add a subtle gradient overlay at the bottom of the image for text readability
            draw = ImageDraw.Draw(canvas, "RGBA")
            for i in range(250):
                alpha = int(i * 1.0)
                draw.line(
                    [(0, img_height - 250 + i), (width, img_height - 250 + i)],
                    fill=(15, 15, 25, alpha),
                )

        except Exception as e:
            print(f"Error processing image {img_path}: {e}")

        draw = ImageDraw.Draw(canvas)

        # Improved Typography and Layout
        try:
            # Try to use a bolder font for title
            title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 90)
            subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 45)
            meta_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 35)
        except:
            title_font = ImageFont.load_default()
            subtitle_font = ImageFont.load_default()
            meta_font = ImageFont.load_default()

        # Text positioning with better hierarchy
        text_start_y = int(height * 0.78)

        # Draw Title (Uppercase for impact)
        draw.text(
            (width // 2, text_start_y),
            title.upper(),
            fill=(255, 255, 255),
            font=title_font,
            anchor="mm",
        )

        # SUBTITLE WRAPPING LOGIC (The Solution for Cut Text)
        subtitle_y = text_start_y + 100
        max_width = width - 160  # Leave margin on both sides

        words = subtitle.split()
        lines = []
        current_line = []

        for word in words:
            test_line = " ".join(current_line + [word])
            # Check length of the line in pixels
            w = draw.textlength(test_line, font=subtitle_font)
            if w <= max_width:
                current_line.append(word)
            else:
                lines.append(" ".join(current_line))
                current_line = [word]
        lines.append(" ".join(current_line))

        # Draw each line
        line_height = 60
        for i, line in enumerate(lines):
            draw.text(
                (width // 2, subtitle_y + (i * line_height)),
                line,
                fill=(180, 180, 200),
                font=subtitle_font,
                anchor="mm",
            )

        # Brand/Session Indicator (Bottom Left)
        draw.text((60, height - 80), f"#{session_id.upper()}", fill=(100, 100, 150), font=meta_font)

        # Sequential Indicator (Bottom Right) - More stylish
        draw.ellipse(
            [width - 150, height - 150, width - 50, height - 50], outline=(100, 100, 255), width=3
        )
        draw.text(
            (width - 100, height - 100),
            f"{frame_num}",
            fill=(255, 255, 255),
            font=title_font,
            anchor="mm",
        )

        output_path = Path("outputs/stories") / f"{session_id}_story_{frame_num}.jpg"
        canvas.save(output_path, "JPEG", quality=95)

        return output_path

    def _crop_to_portrait(
        self, img: Image, target_width: int, target_height: int, img_path: str
    ) -> Image:
        """Crop image to portrait orientation (9:16) using saliency"""
        img_ratio = img.width / img.height
        target_ratio = target_width / target_height

        center_x, center_y = self._get_salient_center(img_path, img.width, img.height)

        if img_ratio > target_ratio:
            # Image is wider, crop width
            new_width = int(img.height * target_ratio)
            left = max(0, min(center_x - new_width // 2, img.width - new_width))
            img = img.crop((left, 0, left + new_width, img.height))
        else:
            # Image is taller, crop height
            new_height = int(img.width / target_ratio)
            top = max(0, min(center_y - new_height // 2, img.height - new_height))
            img = img.crop((0, top, img.width, top + new_height))

        return img
