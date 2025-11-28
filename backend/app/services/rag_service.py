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

    def identify_last_question(self, transcript: str) -> str:
        if not transcript:
            return None
            
        prompt = f"""
        Analyze the following transcript of a sales call. Identify the LAST question asked by the potential client (Lead).
        If no question was asked recently, return "NO_QUESTION".
        Return ONLY the question text.
        
        Transcript:
        {transcript[-2000:]} -- Only look at the recent context
        """
        
        response = self.llm_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1
        )
        
        question = response.choices[0].message.content.strip()
        if "NO_QUESTION" in question:
            return None
        return question

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

    def generate_answer(self, question: str, context_docs: list) -> str:
        context_text = "\n\n".join([doc['content'] for doc in context_docs])
        
        prompt = f"""
        You are a helpful Sales Copilot for financial agents.
        Answer the following question based ONLY on the provided context.
        Keep the answer concise and actionable for the agent to say aloud.
        
        Context:
        {context_text}
        
        Question: {question}
        
        Answer:
        """
        
        response = self.llm_client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3
        )
        return response.choices[0].message.content.strip()

    async def process_assist_request(self, session_id: str):
        transcript = self.get_transcript(session_id)
        if not transcript:
            return {"error": "No transcript found"}
            
        question = self.identify_last_question(transcript)
        if not question:
            return {"status": "no_question_found", "message": "No recent question identified."}
            
        embedding = self.get_embedding(question)
        context_docs = self.search_knowledge_base(embedding)
        
        if not context_docs:
            return {"status": "no_context", "question": question, "answer": "I don't have information on that."}
            
        answer = self.generate_answer(question, context_docs)
        
        return {
            "status": "success",
            "question": question,
            "answer": answer,
            "context": context_docs
        }
