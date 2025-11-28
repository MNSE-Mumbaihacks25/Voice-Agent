import asyncio
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.services.rag_service import RAGService
from app.core.state import transcript_store

async def test_rag():
    # Mock transcript
    session_id = "test_session"
    transcript_store[session_id] = [
        "Hello, I am interested in investing.",
        "Sure, what are you looking for?",
        "I want to know about the HDFC Top 100 Fund.",
        "What is its expense ratio?"
    ]
    
    service = RAGService()
    print("Testing RAG Service...")
    
    # 1. Identify Question
    transcript = service.get_transcript(session_id)
    print(f"Transcript: {transcript}")
    
    question = service.identify_last_question(transcript)
    print(f"Identified Question: {question}")
    
    if not question:
        print("Failed to identify question.")
        return

    # 2. Get Embedding (Mock or Real if keys work)
    try:
        embedding = service.get_embedding(question)
        print(f"Generated Embedding: {len(embedding)} dimensions")
    except Exception as e:
        print(f"Embedding failed (expected if keys are invalid): {e}")
        # Mock embedding for next step
        embedding = [0.1] * 1536

    # 3. Search Knowledge Base
    try:
        docs = service.search_knowledge_base(embedding)
        print(f"Found {len(docs)} documents.")
        for doc in docs:
            print(f"- {doc['content'][:50]}...")
    except Exception as e:
        print(f"Search failed: {e}")
        docs = [{"content": "HDFC Top 100 Fund has an expense ratio of 1.15%."}]

    # 4. Generate Answer
    try:
        answer = service.generate_answer(question, docs)
        print(f"Generated Answer: {answer}")
    except Exception as e:
        print(f"Answer generation failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_rag())
