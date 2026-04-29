from google import genai
from typing import List, Dict, Optional
from app.config import settings
from PIL import Image
import io


import json


class GeminiService:
    """Google Gemini 3.1 Pro integration for multimodal content generation"""

    def __init__(self):
        """Initialize Gemini client"""
        try:
            self.client = genai.Client(api_key=settings.gemini_api_key)
            print("Gemini 3.1 Pro initialized successfully")
        except Exception as e:
            print(f"Error initializing Gemini: {e}")
            self.client = None

    def generate_linkedin_caption(
        self, event_name: str, selected_assets: List[Dict], analysis_data: Dict
    ) -> str:
        """
        Generate professional LinkedIn caption for event

        Args:
            event_name: Name of the event
            selected_assets: List of selected asset metadata
            analysis_data: Analysis data from the session

        Returns:
            str: Generated LinkedIn caption
        """
        if not self.client:
            return "Gemini service unavailable"

        try:
            # Extract key insights from analysis
            stats = analysis_data.get("selection_stats", {})
            people_count = stats.get("hero_count", 0) + stats.get("action_count", 0)

            prompt = f"""
            Write a professional LinkedIn post for the event: {event_name}
            
            Context:
            - {stats.get('total_assets', 0)} total media assets captured
            - {people_count} high-quality shots selected
            - High crowd engagement detected
            - Professional event photography
            
            Requirements:
            - Professional and business-focused tone
            - 2-3 paragraphs
            - Include relevant hashtags (3-5)
            - Focus on networking, engagement, and professional atmosphere
            - Sound like someone who actually attended
            - Include a call-to-action for engagement
            """

            response = self.client.models.generate_content(model="gemini-1.5-pro", contents=prompt)
            return response.text

        except Exception as e:
            print(f"Error generating LinkedIn caption: {e}")
            return f"Excited to share highlights from {event_name}! Great energy and engagement throughout the event. #Networking #Events"

    def generate_instagram_caption(
        self, event_name: str, selected_assets: List[Dict], analysis_data: Dict
    ) -> str:
        """
        Generate Instagram caption (distinct from LinkedIn)

        Args:
            event_name: Name of the event
            selected_assets: List of selected asset metadata
            analysis_data: Analysis data from the session

        Returns:
            str: Generated Instagram caption
        """
        if not self.client:
            return "Gemini service unavailable"

        try:
            stats = analysis_data.get("selection_stats", {})

            prompt = f"""
            Write an engaging Instagram caption for the event: {event_name}
            
            Context:
            - {stats.get('total_assets', 0)} photos/videos captured
            - Amazing crowd energy and vibes
            - Memorable moments throughout
            
            Requirements:
            - Casual, fun, and energetic tone
            - 1-2 short paragraphs
            - Include emojis (5-8)
            - Include relevant hashtags (8-12)
            - Focus on experience, vibes, and memorable moments
            - Sound authentic and relatable
            - Different from LinkedIn - more casual and visual-focused
            """

            response = self.client.models.generate_content(
                model="gemini-flash-latest", contents=prompt
            )
            return response.text

        except Exception as e:
            print(f"Error generating Instagram caption: {e}")
            return f"Amazing vibes at {event_name}! ✨ What a night to remember! 🎉 #EventVibes #GoodTimes"

    def generate_case_study(
        self, event_name: str, selected_assets: List[Dict], analysis_data: Dict
    ) -> Dict:
        """
        Generate structured case study draft

        Args:
            event_name: Name of the event
            selected_assets: List of selected asset metadata
            analysis_data: Analysis data from the session

        Returns:
            Dict with case study sections
        """
        if not self.client:
            return {"error": "Gemini service unavailable"}

        try:
            stats = analysis_data.get("selection_stats", {})

            prompt = f"""
            Generate a structured case study for the event: {event_name}
            
            Context:
            - {stats.get('total_assets', 0)} media assets captured
            - {stats.get('selected_count', 0)} high-quality assets selected
            - {stats.get('hero_count', 0)} hero shots identified
            - High engagement and energy detected
            
            Generate the following sections:
            1. Executive Summary (2-3 sentences)
            2. Engagement Summary (describe crowd energy and participation)
            3. Sponsor Visibility (mention brand presence and visibility)
            4. Key Moments (list 3-5 memorable moments from the event)
            
            Format as JSON with keys: executive_summary, engagement_summary, sponsor_visibility, key_moments
            """

            response = self.client.models.generate_content(
                model="gemini-flash-latest",
                contents=prompt,
                config={"response_mime_type": "application/json"},
            )

            return json.loads(response.text)

        except Exception as e:
            print(f"Error generating case study: {e}")
            return {
                "executive_summary": f"Successful execution of {event_name}",
                "engagement_summary": "High crowd engagement throughout",
                "sponsor_visibility": "Strong brand presence",
                "key_moments": ["Opening ceremony", "Key moments", "Closing"],
            }

    def analyze_images_multimodal(self, image_paths: List[str], prompt: str) -> str:
        """
        Analyze multiple images using Gemini's multimodal capabilities

        Args:
            image_paths: List of image file paths
            prompt: Analysis prompt

        Returns:
            str: Analysis result
        """
        if not self.client:
            return "Gemini service unavailable"

        try:
            # Load images
            images = []
            for path in image_paths:
                img = Image.open(path)
                images.append(img)

            # Create multimodal prompt
            content = [prompt] + images

            response = self.client.models.generate_content(
                model="gemini-flash-latest", contents=content
            )
            return response.text

        except Exception as e:
            print(f"Error in multimodal analysis: {e}")
            return "Analysis failed"

    def generate_story_text(
        self, event_name: str, frame_index: int, total_frames: int, asset_data: Dict
    ) -> str:
        """
        Generate text overlay for Instagram story frame

        Args:
            event_name: Name of the event
            frame_index: Current frame index
            total_frames: Total number of frames
            asset_data: Asset analysis data

        Returns:
            str: Generated text overlay
        """
        if not self.client:
            return f"{event_name} - Frame {frame_index + 1}"

        try:
            emotions = asset_data.get("analysis", {}).get("emotions", {})
            dominant_emotion = (
                max(emotions.items(), key=lambda x: x[1])[0] if emotions else "neutral"
            )

            prompt = f"""
            Generate a short, punchy text overlay for Instagram story frame {frame_index + 1} of {total_frames}
            
            Event: {event_name}
            Mood: {dominant_emotion}
            
            Requirements:
            - Punchy and short
            - Maximum 5-7 words
            """

            response = self.client.models.generate_content(
                model="gemini-flash-latest", contents=prompt
            )
            return response.text.strip()

        except Exception as e:
            print(f"Error generating story text: {e}")
            return f"{event_name} Highlights"

    def refine_content(self, content: str, platform: str, feedback: str) -> str:
        """
        Refine generated content based on feedback

        Args:
            content: Original content
            platform: Target platform
            feedback: User feedback for improvement

        Returns:
            str: Refined content
        """
        if not self.client:
            return content

        try:
            prompt = f"""
            Refine the following {platform} content based on this feedback: "{feedback}"
            
            Original Content:
            {content}
            
            Requirements:
            - Maintain the same platform-specific tone
            - Address the feedback precisely
            - Output ONLY the refined content
            """

            response = self.client.models.generate_content(
                model="gemini-flash-latest", contents=prompt
            )
            return response.text.strip()

        except Exception as e:
            print(f"Error refining content: {e}")
            return content


# Singleton instance
gemini_service = GeminiService()
