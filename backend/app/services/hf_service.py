import logging
import os
import requests
from app.core.config import settings

logger = logging.getLogger(__name__)

class HuggingFaceService:
    def __init__(self):
        self.api_url = "https://api-inference.huggingface.co/models/openai/whisper-large-v2"
        self.headers = {
            "Authorization": f"Bearer {settings.HF_TOKEN}",
            "Content-Type": "audio/webm" 
        }

    async def transcribe_audio(self, audio_bytes: bytes) -> str:
        """
        Transcribes audio bytes using Hugging Face Inference API via direct HTTP request.
        """
        try:
            response = requests.post(
                self.api_url,
                headers=self.headers,
                data=audio_bytes
            )
            
            if response.status_code != 200:
                logger.error(f"HF Error {response.status_code}: {response.text}")
                return ""
                
            result = response.json()
            
            if 'text' in result:
                return result['text']
            else:
                return str(result)

        except Exception as e:
            logger.error(f"HF Transcription Error: {e}")
            print(f"HF Transcription Error: {e}")
            return ""
