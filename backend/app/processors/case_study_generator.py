"""
Case Study Generator: Creates structured case study documents
using Gemini to synthesize event assets and generated copy.
"""

from pathlib import Path
from typing import List, Dict
from datetime import datetime
import json
from app.config import settings


class CaseStudyGenerator:
    def __init__(self):
        self.gemini_api_key = settings.gemini_api_key

    def generate(
        self, assets: List[Dict], copies: Dict[str, str], dataset_name: str, session_id: str
    ) -> Path:
        """Generate a structured case study document"""

        event_name = dataset_name.replace("event_dataset_", "").replace("_", " ").title()

        # Prepare data for LLM
        avg_score = self._avg_score(assets)
        total_assets = len(assets)
        high_quality_count = sum(1 for a in assets if a.get("score", 0) > 0.7)

        # Extract metadata summaries
        total_people = sum(a.get("metadata", {}).get("people_count", 0) for a in assets)
        total_engaged = sum(a.get("metadata", {}).get("engaged_faces", 0) for a in assets)

        asset_summary = [
            f"Image {i+1} (Score: {a['score']:.2f}): {a.get('rationale', 'Good quality')}"
            for i, a in enumerate(assets[:10])
        ]

        if self.gemini_api_key:
            try:
                content = self._generate_with_gemini(
                    event_name,
                    total_assets,
                    avg_score,
                    high_quality_count,
                    total_people,
                    total_engaged,
                    asset_summary,
                    copies,
                )
            except Exception as e:
                print(f"Gemini API failed for case study: {e}")
                content = self._fallback_template(event_name, assets, copies)
        else:
            content = self._fallback_template(event_name, assets, copies)

        # Save to file
        output_dir = Path("outputs/case_studies")
        output_dir.mkdir(parents=True, exist_ok=True)
        output_path = output_dir / f"{session_id}_case_study.txt"

        with open(output_path, "w") as f:
            f.write(content)

        return output_path

    def _generate_with_gemini(
        self,
        event_name,
        total_assets,
        avg_score,
        high_quality,
        total_people,
        total_engaged,
        asset_summary,
        copies,
    ):
        from google import genai

        client = genai.Client(api_key=self.gemini_api_key)

        prompt = f"""
        You are an elite experiential marketing strategist for 'StepOne'. 
        Write a professional, human-centric Case Study for the event: "{event_name}".
        
        CONTEXT FROM HACKATHON BRIEF:
        - Venue: Bharat Mandapam
        - Scale: 1,200+ delegates
        - Key VIP: Chief Guest Shri Nitin Gadkari
        - Focus: Sustainability, Innovation, Global Metal Trade
        - StepOne Role: End-to-end ops, Stage Design, AV/Lighting, Protocol management.
        
        AI DATA POINTS (Use these for the 'Results' section):
        - Total Assets Processed: {total_assets}
        - High Quality Assets Selected: {high_quality}
        - AI Quality Score: {avg_score:.2f}/1.0
        - Attendee Engagement: {total_engaged} high-energy moments detected.
        
        STRUCTURE REQUIREMENT (DO NOT use bullet points, tell a STORY):
        1. INTRODUCTION: About BME, the venue (Bharat Mandapam), and the massive scale.
        2. THE PROBLEM: Detail the challenges of managing 1,200+ delegates and strict security protocol for VIPs like Nitin Gadkari.
        3. THE IDEA: How StepOne designed the flow to balance a high-level summit with a busy industry expo.
        4. THE APPROACH: Describe the operational precision, lighting/AV coordination, and protocol management.
        5. THE EXECUTION: The story of the event days—from the Global CEO Forum to the launch of Vision 2030.
        6. RESULTS: Use the AI metrics ({total_assets} assets, {total_engaged} energy points) to prove success and ROI.
        
        TONE: Clear, simple, human, and professional. Avoid jargon.
        """

        response = client.models.generate_content(model="gemini-1.5-pro", contents=prompt)
        return response.text

    def _fallback_template(self, event_name, assets, copies):
        """Fallback template if API fails"""
        return f"""
{'='*60}
CASE STUDY: {event_name}
{'='*60}

Executive Summary
-----------------
This case study analyzes the {event_name} event, documenting key moments,
attendee engagement, and brand visibility based on fallback logic.

Event Details
-------------
Event Name: {event_name}
Date: {datetime.now().strftime('%B %d, %Y')}
Total Assets Processed: {len(assets)}
Image Quality Score: {self._avg_score(assets):.2f}/1.0

Marketing Outputs
-----------------
LinkedIn Post:
{copies.get('linkedin', 'N/A')}

Instagram Caption:
{copies.get('instagram', 'N/A')}

{'='*60}
END OF CASE STUDY
{'='*60}
"""

    def _avg_score(self, assets: List[Dict]) -> float:
        """Calculate average score of assets"""
        if not assets:
            return 0.0
        scores = [a.get("score", 0) for a in assets]
        return sum(scores) / len(scores)
