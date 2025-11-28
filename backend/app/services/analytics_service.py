from openai import OpenAI
from app.core.config import settings
from app.core.state import transcript_store
import logging
import os
import json

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self):
        self.llm_client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY
        )

    async def diarize_audio(self, session_id: str):
        """
        Mock Pyannote Diarization.
        Real implementation would load the pipeline and process 'audio_{session_id}.wav'.
        """
        filename = f"audio_{session_id}.wav"
        if not os.path.exists(filename):
            logger.warning(f"Audio file {filename} not found.")
            # Fallback to stored transcript without speaker labels
            return transcript_store.get(session_id, [])

        # Placeholder for Pyannote logic
        # try:
        #     from pyannote.audio import Pipeline
        #     pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization-3.1", use_auth_token="HF_TOKEN")
        #     diarization = pipeline(filename)
        #     # Convert diarization to text segments...
        # except: ...
        
        logger.info("Simulating Pyannote Diarization...")
        # For now, return the raw transcript as a single block or mock speakers
        # In a real app, we'd align the text with the diarization timestamps.
        raw_transcript = transcript_store.get(session_id, [])
        return raw_transcript

    async def generate_report(self, session_id: str):
        diarized_data = await self.diarize_audio(session_id)
        transcript_text = "\n".join(diarized_data)
        
        if not transcript_text:
            return {"error": "No transcript available"}
            
        prompt = f"""
        Analyze the following sales call transcript.
        Generate a JSON report with the following fields:
        - sentiment: (Positive/Neutral/Negative)
        - objections: [List of objections raised by the lead]
        - adherence: (Did the agent mention disclaimers? Yes/No)
        - next_steps: [List of actionable items]
        
        Transcript:
        {transcript_text}
        
        Return ONLY valid JSON.
        """
        
        response = self.llm_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )
        
        report = json.loads(response.choices[0].message.content)
        return report
