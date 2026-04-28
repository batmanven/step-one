"""
Copy Generator: Generates platform-specific copy using true
visual grounding with Gemini Vision models.
"""
import os
from typing import Dict, List
from pathlib import Path
from PIL import Image

class CopyGenerator:
    def __init__(self):
        self.gemini_api_key = os.environ.get("GEMINI_API_KEY")
    
    def generate_all(self, selected_assets: List[Dict], dataset_name: str) -> Dict[str, str]:
        """Generate copy for LinkedIn and Instagram"""
        
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
        
        return {
            "linkedin": linkedin,
            "instagram": instagram
        }
    
    def _generate_with_gemini(self, selected_assets: List[Dict], event_name: str) -> Dict[str, str]:
        """Generate copy using Gemini Vision with Visual Grounding"""
        import google.generativeai as genai
        
        genai.configure(api_key=self.gemini_api_key)
        # Use gemini-1.5-flash for speed and multimodal capabilities
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Prepare the visual context
        images = []
        for asset in selected_assets[:4]:  # Take top 4 images for context
            try:
                img = Image.open(asset["path"])
                # Convert to RGB to ensure compatibility
                if img.mode != 'RGB':
                    img = img.convert('RGB')
                # Resize slightly to save bandwidth/tokens while keeping semantics
                img.thumbnail((1024, 1024))
                images.append(img)
            except Exception as e:
                print(f"Failed to load image for Gemini: {e}")

        # LinkedIn Prompt
        linkedin_prompt = f"""
        You are an experiential marketing professional writing a LinkedIn post.
        You attended the event: "{event_name}".
        
        CRITICAL INSTRUCTION: I have attached photos from the event. You MUST write the post based on what is ACTUALLY visible in these photos. 
        - If you see a crowded audience, mention the great turnout.
        - If you see a speaker on stage, mention the keynote or panel.
        - If you see networking, mention the connections made.
        DO NOT hallucinate details that are not in the photos.
        
        Tone: Professional, insightful, 200-300 words.
        Format: Include 3 bullet points of highlights derived from the images.
        Add 3-4 hashtags at the end.
        """
        
        linkedin_content = [linkedin_prompt] + images
        linkedin_response = model.generate_content(linkedin_content)
        
        # Instagram Prompt
        instagram_prompt = f"""
        You are an event attendee posting an Instagram caption about "{event_name}".
        
        CRITICAL INSTRUCTION: Look at the attached photos. Describe the VIBE and energy based strictly on what you see in the images.
        
        Tone: Fun, visual, emoji-rich, 100-150 words.
        Start with an emoji. Add 4-5 relevant hashtags at the end.
        """
        
        instagram_content = [instagram_prompt] + images
        instagram_response = model.generate_content(instagram_content)
        
        return {
            "linkedin": linkedin_response.text.strip(),
            "instagram": instagram_response.text.strip()
        }
