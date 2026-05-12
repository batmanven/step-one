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
                {"title": "VIP Spotlight", "subtitle": "Industry leaders sharing vision"},
                {"title": "Panel Discussion", "subtitle": "Deep technical insights shared"},
                {"title": "Vision 2030", "subtitle": "Shaping the future of metals"},
                {"title": "Networking", "subtitle": "Connecting with global peers"},
                {"title": "Ceremony", "subtitle": "Honoring excellence in sector"},
                {"title": "Memories Made", "subtitle": "Unforgettable moments captured"},
            ]
        )

        return {"linkedin": linkedin, "instagram": instagram, "stories_json": stories}

    def _generate_with_gemini(self, selected_assets: List[Dict], event_name: str) -> Dict[str, str]:
        """Generate copy using Gemini Vision with Visual Grounding"""
        from google import genai

        client = genai.Client(api_key=self.gemini_api_key)

        # Prepare the visual context
        images = []
        for asset in selected_assets[:8]:  # Take top 8 images for richer context
            try:
                img = Image.open(asset["path"])
                if img.mode != "RGB":
                    img = img.convert("RGB")
                img.thumbnail((1024, 1024))
                images.append(img)
            except Exception as e:
                print(f"Failed to load image for Gemini: {e}")

        # Bulk Prompt to save API calls
        prompt = f"""
        You are an elite experiential marketing professional covering the event: "{event_name}".
        
        CRITICAL INSTRUCTION: I have attached several photos from the event. You MUST write all content based strictly on what is ACTUALLY visible in these photos. 
        DO NOT hallucinate details. 

        Please generate three pieces of content and return them exactly in the following JSON format. Do not include markdown code blocks (```json), just raw JSON:
        {{
            "linkedin": "Your 200-word professional post with 3 bullet points and hashtags.",
            "instagram": "Your 100-word fun, visual, emoji-rich caption with hashtags.",
            "stories": [
                {{"title": "Frame 1 Title", "subtitle": "Sentence about event opening"}},
                {{"title": "Frame 2 Title", "subtitle": "Sentence about technical insights"}},
                {{"title": "Frame 3 Title", "subtitle": "Sentence about keynote energy"}},
                {{"title": "Frame 4 Title", "subtitle": "Sentence about networking"}},
                {{"title": "Frame 5 Title", "subtitle": "Sentence about panel discussions"}},
                {{"title": "Frame 6 Title", "subtitle": "Sentence about crowd engagement"}},
                {{"title": "Frame 7 Title", "subtitle": "Sentence about ceremony/awards"}},
                {{"title": "Frame 8 Title", "subtitle": "Sentence about event closing/legacy"}}
            ]
        }}
        """

        # Use a type-safe list for the Gemini SDK
        contents: list = [prompt]
        contents.extend(images)
        
        response = client.models.generate_content(
            model="gemini-flash-latest", 
            contents=contents
        )

        if not response.text:
            print("Gemini returned an empty response, falling back to templates.")
            return self._generate_with_templates(event_name)
            
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
