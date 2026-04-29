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
        You are an elite marketing analyst. Write a professional Case Study for the experiential marketing event: "{event_name}".
        
        Use the following ACTUAL DATA gathered by our AI pipeline to write a factual, data-driven report. Do not hallucinate details outside of this data.
        
        DATA POINTS:
        - Total Assets Processed: {total_assets}
        - High Quality Assets Selected: {high_quality}
        - Average AI Quality Score: {avg_score:.2f}/1.0
        - Total People Detected in Top Assets: {total_people}
        - Highly Engaged/Smiling Faces Detected: {total_engaged}
        
        ASSET RATIONALES (What the AI saw):
        {chr(10).join(asset_summary)}
        
        GENERATED COPY:
        LinkedIn: {copies.get('linkedin', 'N/A')}
        Instagram: {copies.get('instagram', 'N/A')}
        
        FORMAT REQUIREMENT:
        Create a beautiful, text-based report with the following sections (use markdown-style headers like === and ---):
        1. Executive Summary
        2. Event & Engagement Metrics (Incorporate the people/faces data here)
        3. Visual Content Analysis (Summarize the asset rationales)
        4. Marketing Outputs (Include the exact generated copy)
        5. Conclusion & ROI Recommendations
        
        Tone: Analytical, confident, professional.
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
