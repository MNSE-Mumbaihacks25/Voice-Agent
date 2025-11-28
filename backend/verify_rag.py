import asyncio
import os
from dotenv import load_dotenv
from app.services.rag_service import RAGService
from app.core.state import transcript_store

# Load env vars
load_dotenv()

async def verify():
    print("Verifying Mutual Funds RAG...")
    
    rag = RAGService()
    
    # Test 1: Implicit Recommendation Intent
    session_id = "test_session_1"
    # Implicit intent: "I want to save for retirement" -> Should trigger "Suggest retirement fund"
    transcript_store[session_id] = ["Agent: Hello.", "Lead: I am 35 and I want to start saving for my retirement. I can invest 5k a month."]
    
    print("\n--- Test 1: Implicit Intent (Retirement) ---")
    result = await rag.process_assist_request(session_id)
    print(f"Detected Intent: {result.get('question')}")
    print(f"Answer: {result.get('answer')}")
    
    # Test 2: Information Intent
    session_id_2 = "test_session_2"
    transcript_store[session_id_2] = ["Lead: Tell me about the Aditya Birla SL Frontline Equity Fund."]
    
    print("\n--- Test 2: Information Intent ---")
    result_2 = await rag.process_assist_request(session_id_2)
    print(f"Detected Intent: {result_2.get('question')}")
    print(f"Answer: {result_2.get('answer')}")
    
    # Test 3: No Intent (Small Talk)
    session_id_3 = "test_session_3"
    transcript_store[session_id_3] = ["Agent: How are you?", "Lead: I am good, thanks. How about you?"]
    
    # Test 4: Valid Trigger
    session_id_4 = "test_session_4"
    transcript_store[session_id_4] = ["Lead: I need a good fund.", "Agent: Let me check that for you."]
    
    print("\n--- Test 4: Valid Trigger ---")
    result_4 = await rag.process_assist_request(session_id_4, trigger_word="Let me check")
    print(f"Status: {result_4.get('status')}")
    print(f"Intent: {result_4.get('question')}")
    
    # Test 5: Invalid Trigger
    session_id_5 = "test_session_5"
    transcript_store[session_id_5] = ["Agent: Let me check the time."]
    
    print("\n--- Test 5: Invalid Trigger ---")
    result_5 = await rag.process_assist_request(session_id_5, trigger_word="Let me check")
    print(f"Status: {result_5.get('status')}")
    print(f"Message: {result_5.get('message')}")

if __name__ == "__main__":
    asyncio.run(verify())
