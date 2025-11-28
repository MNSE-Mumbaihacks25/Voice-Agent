import logging
from langchain_groq import ChatGroq
from app.core.config import settings

logger = logging.getLogger(__name__)

class SummaryService:
    def __init__(self):
        self.llm_client = ChatGroq(
            temperature=0,
            model_name="llama-3.1-8b-instant",
            api_key=settings.GROQ_API_KEY
        )

    async def generate_summary(self, transcript: str, lead_name: str = "Lead") -> str:
        if not transcript:
            return "No transcript available."

        prompt = f"""
        You are an expert Summarizing Agent for financial sales calls.
        Summarize the following conversation between an Agent and {lead_name}.
        
        Focus on:
        1. Key topics discussed (e.g., specific funds, retirement goals).
        2. {lead_name}'s sentiment and key concerns.
        3. Action items or next steps agreed upon.
        
        Keep the summary concise (max 3-4 sentences).
        
        Transcript:
        {transcript}
        
        Summary:
        """
        
        try:
            response = self.llm_client.invoke(prompt)
            return response.content.strip()
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return "Failed to generate summary."
