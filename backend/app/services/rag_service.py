from openai import OpenAI
from supabase import create_client, Client
from app.core.config import settings
from app.core.state import transcript_store
import logging
import json

logger = logging.getLogger(__name__)

from langchain_google_genai import GoogleGenerativeAIEmbeddings

class RAGService:
    def __init__(self):
        # Groq Client (via OpenAI SDK)
        self.llm_client = OpenAI(
            base_url="https://api.groq.com/openai/v1",
            api_key=settings.GROQ_API_KEY
        )
        # Embedding Client (Google Gemini)
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/text-embedding-004",
            google_api_key=settings.GOOGLE_API_KEY
        )
        
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    def get_transcript(self, session_id: str) -> str:
        return " ".join(transcript_store.get(session_id, []))

    def assess_user_intent(self, transcript: str) -> str:
        if not transcript:
            return None
            
        prompt = f"""
        You are a smart "Listening Agent" for a financial sales call.
        Your goal is to analyze the transcript and gauge the potential client's (Lead) INTENT.
        
        Determine if the Lead is expressing an intent that requires information from the Knowledge Base (Mutual Funds data or Policy).
        
        Intents to Detect:
        1. **Recommendation**: Wants a suggestion (e.g., "What fund is good for retirement?", "Suggest a mid-cap fund").
        2. **Information**: Wants specific details (e.g., "What is the return of Axis Bluechip?", "Tell me about this fund").
        3. **Comparison**: Wants to compare options (e.g., "Which is better, X or Y?").
        4. **Objection/Concern**: Expressing a worry that needs addressing (e.g., "Is this safe?", "The fees seem high").
        5. **Goal/Need**: Stating a financial goal that implies a need for a product (e.g., "I want to save for retirement", "I have 5k to invest").
        
        Instructions:
        - Look at the RECENT context (last few turns).
        - If the user states a **Goal** (e.g., "I want to save for X"), treat it as a **Recommendation** intent (Query: "funds for X").
        - If an intent is detected, formulate a concise **Search Query** that captures the core need.
        - If NO clear intent is detected (e.g., small talk, greeting, simple acknowledgement), return "NO_INTENT".
        - Return ONLY the Search Query or "NO_INTENT".
        
        Transcript:
        {transcript[-2000:]}
        """
        
        response = self.llm_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        result = response.choices[0].message.content.strip()
        if "NO_INTENT" in result:
            return None
        return result

    def get_embedding(self, text: str):
        # Using Google Gemini Embeddings
        return self.embeddings.embed_query(text)

    def search_knowledge_base(self, query_embedding):
        response = self.supabase.rpc(
            "match_documents",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.5,
                "match_count": 3
            }
        ).execute()
        return response.data

    def search_mutual_funds(self, query_embedding):
        response = self.supabase.rpc(
            "match_mutual_funds",
            {
                "query_embedding": query_embedding,
                "match_threshold": 0.3, # Lower threshold for broader matching
                "match_count": 5
            }
        ).execute()
        return response.data

    def generate_answer(self, question: str, context_docs: list, transcript: str = "") -> str:
        # Check if context is from mutual funds or generic KB
        context_text = ""
        for doc in context_docs:
            if 'scheme_name' in doc:
                # It's a mutual fund
                context_text += f"Fund: {doc['scheme_name']}\nCategory: {doc['category']}\nReturns (1Y): {doc['returns_1yr']}%\nDetails: {doc['metadata']}\n\n"
            else:
                # Generic KB
                context_text += f"{doc['content']}\n\n"
        
        prompt = f"""
        You are a helpful, sincere, and positive Sales Copilot for financial agents.
        Your goal is to help the agent close the sale while maintaining a warm and trustworthy relationship with the customer.
        
        Instructions:
        1. Answer the User's Intent based ONLY on the provided Knowledge Base Context (Mutual Funds or Policy).
        2. Use the Conversation History to understand the flow.
        3. Tone: Sincere, Positive, Professional, and Helpful. Avoid being pushy or robotic.
        4. If recommending a fund, mention its name, category, and why it fits (e.g., returns).
        5. Keep the answer concise and actionable for the agent to say aloud.

        Conversation History:
        {transcript}
        
        Knowledge Base Context:
        {context_text}
        
        User Intent/Query: {question}
        
        Suggested Answer (for the Agent to say):
        """
        
        response = self.llm_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    def verify_trigger_context(self, transcript: str, trigger_word: str) -> bool:
        if not transcript or not trigger_word:
            return False
            
        prompt = f"""
        You are a context analyzer for a sales call.
        The Agent just said the trigger phrase: "{trigger_word}".
        
        Analyze the transcript to determine if the Agent is using this phrase to signal they are about to look up information for the Lead (Valid).
        
        Valid Examples:
        - "Let me check that fund for you."
        - "Let me check the returns."
        - "One moment, let me check." (After Lead asked a question)
        
        Invalid Examples:
        - "Let me check the time."
        - "Let me check if I left the stove on."
        - "Let me check my email."
        
        Transcript:
        {transcript[-1000:]}
        
        Is this a VALID lookup intent? Return ONLY "YES" or "NO".
        """
        
        response = self.llm_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0
        )
        
        result = response.choices[0].message.content.strip().upper()
        return "YES" in result

    async def process_assist_request(self, session_id: str, trigger_word: str = None):
        transcript = self.get_transcript(session_id)
        if not transcript:
            return {"error": "No transcript found"}
            
        # Verify Trigger if provided
        if trigger_word:
            is_valid = self.verify_trigger_context(transcript, trigger_word)
            if not is_valid:
                return {"status": "ignored", "message": f"Trigger '{trigger_word}' context was invalid."}
            
        # Assess Intent instead of just finding a question
        search_query = self.assess_user_intent(transcript)
        
        if not search_query:
            return {"status": "no_intent_detected", "message": "No actionable intent identified."}
            
        embedding = self.get_embedding(search_query)
        
        # Search both KB and Mutual Funds
        kb_docs = self.search_knowledge_base(embedding)
        fund_docs = self.search_mutual_funds(embedding)
        
        # Combine results
        context_docs = kb_docs + fund_docs
        
        if not context_docs:
            return {"status": "no_context", "question": search_query, "answer": "I don't have information on that."}
            
        answer = self.generate_answer(search_query, context_docs, transcript)
        
        return {
            "status": "success",
            "question": search_query,
            "answer": answer,
            "context": context_docs
        }
