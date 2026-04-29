"""
Copy Generator: Generates platform-specific copy using true
visual grounding with Gemini Vision models.
"""

from typing import Dict, List
from pathlib import Path
from PIL import Image
import json
from app.config import settings


class CopyGenerator:
    def __init__(self):
        self.gemini_api_key = settings.gemini_api_key

    def generate_all(self, selected_assets: List[Dict], dataset_name: str) -> Dict[str, str]:
        """Generate copy for LinkedIn, Instagram, and Stories"""

        event_name = self._extract_event_name(dataset_name)

        if self.gemini_api_key:
            try:
                return self._generate_with_gemini(selected_assets, event_name)
            except Exception as e:
                print(f"Gemini API failed: {e}, falling back to templates")

        return self._generate_with_templates(event_name)

    def _extract_event_name(self, dataset_name: str) -> str:
        """Extract readable event name from dataset folder name"""
        name = dataset_name.replace("event_dataset_", "").replace("_", " ")
        return name.title()

    def _generate_with_templates(self, event_name: str) -> Dict[str, str]:
        """Fallback template generation"""
        linkedin = f"""Had an incredible time at {event_name}! 

The energy in the room was amazing, with industry leaders sharing insights and networking opportunities that will shape the future.

Key highlights:
• Engaging presentations from thought leaders
• Valuable networking with industry peers  
• Hands-on workshops and interactive sessions

Events like these remind me why I love being part of this community. Looking forward to implementing these learnings!

#EventRecap #{event_name.replace(' ', '')} #Networking #Innovation"""

        instagram = f"""✨ {event_name} vibes! 

What an amazing experience filled with learning, networking, and inspiration! 

Swipe to see the highlights →

#EventLife #{event_name.replace(' ', '')} #GoodTimes #Networking #Innovation"""

        stories = json.dumps(
            [
                {"title": "The Event Begins", "subtitle": "Excitement fills the room"},
                {"title": "Key Moments", "subtitle": "Powerful presentations"},
                {"title": "Networking", "subtitle": "Connecting with leaders"},
                {"title": "Memories Made", "subtitle": "Unforgettable moments"},
            ]
        )

        return {"linkedin": linkedin, "instagram": instagram, "stories_json": stories}

    def _generate_with_gemini(self, selected_assets: List[Dict], event_name: str) -> Dict[str, str]:
        """Generate copy using Gemini Vision with Visual Grounding"""
        from google import genai

        client = genai.Client(api_key=self.gemini_api_key)

        # Prepare the visual context
        images = []
        for asset in selected_assets[:4]:  # Take top 4 images for context
            try:
                img = Image.open(asset["path"])
                # Convert to RGB to ensure compatibility
                if img.mode != "RGB":
                    img = img.convert("RGB")
                # Resize slightly to save bandwidth/tokens while keeping semantics
                img.thumbnail((1024, 1024))
                images.append(img)
            except Exception as e:
                print(f"Failed to load image for Gemini: {e}")

        # Bulk Prompt to save API calls
        prompt = f"""
        You are an elite experiential marketing professional covering the event: "{event_name}".
        
        CRITICAL INSTRUCTION: I have attached 4 photos from the event. You MUST write all content based strictly on what is ACTUALLY visible in these photos. 
        DO NOT hallucinate details. If there is a panel, mention it. If there is a crowd, mention the turnout.

        Please generate three pieces of content and return them exactly in the following JSON format. Do not include markdown code blocks (```json), just raw JSON:
        {{
            "linkedin": "Your 200-word professional post with 3 bullet points and hashtags.",
            "instagram": "Your 100-word fun, visual, emoji-rich caption with hashtags.",
            "stories": [
                {{"title": "Short punchy title for frame 1 (max 15 chars)", "subtitle": "A complete sentence describing the excitement of the event opening"}},
                {{"title": "Title for frame 2", "subtitle": "A sentence focusing on the deep learning and technical insights shared"}},
                {{"title": "Title for frame 3", "subtitle": "A sentence about the networking energy and community connections"}},
                {{"title": "Title for frame 4", "subtitle": "A concluding sentence about the lasting impact of the event"}}
            ]
        }}
        """

        content = [prompt] + images
        response = client.models.generate_content(model="gemini-flash-latest", contents=content)

        text_resp = response.text.strip()
        if text_resp.startswith("```json"):
            text_resp = text_resp.replace("```json", "").replace("```", "").strip()

        try:
            data = json.loads(text_resp)
            return {
                "linkedin": data.get("linkedin", ""),
                "instagram": data.get("instagram", ""),
                "stories_json": json.dumps(data.get("stories", [])),
            }
        except Exception as e:
            print(f"Failed to parse JSON from Gemini: {e}")
            return self._generate_with_templates(event_name)
