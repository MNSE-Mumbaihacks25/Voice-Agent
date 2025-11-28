import asyncio
import os
from dotenv import load_dotenv
from app.services.rag_service import RAGService
from app.core.state import transcript_store

# Load env vars
load_dotenv()

async def simulate():
    print("Simulating Conversation: John (Agent) vs Karen (Investor)\n")
    
    rag = RAGService()
    session_id = "sim_session_1"
    transcript_store[session_id] = []
    
    conversation = [
        {"speaker": "John", "text": "Hello Karen, how are you doing today?"},
        {"speaker": "Karen", "text": "I'm good John. I wanted to discuss some investment options for my retirement."},
        {"speaker": "John", "text": "That's a great goal. We have some excellent pension funds."},
        {"speaker": "Karen", "text": "Can you suggest a good one? I have about 10k to invest monthly."},
        {"speaker": "John", "text": "Sure, let me check the best retirement funds for you.", "trigger": "let me check"},
        {"speaker": "Karen", "text": "Also, I heard about the Aditya Birla Frontline Equity Fund. How is that?"},
        {"speaker": "John", "text": "Let me check the details for that fund.", "trigger": "let me check"},
        {"speaker": "John", "text": "By the way, let me check the time, I have another meeting soon.", "trigger": "let me check"}
    ]
    
    for turn in conversation:
        # 1. Add to transcript
        line = f"{turn['speaker']}: {turn['text']}"
        transcript_store[session_id].append(line)
        print(f"[{turn['speaker']}]: {turn['text']}")
        
        # 2. Check for Trigger
        if "trigger" in turn:
            trigger_word = turn["trigger"]
            print(f"   >>> Trigger Detected: '{trigger_word}'")
            
            # Call RAG
            result = await rag.process_assist_request(session_id, trigger_word=trigger_word)
            
            if result.get("status") == "success":
                print(f"   [RAG] Intent: {result.get('question')}")
                print(f"   [RAG] Answer: {result.get('answer')[:200]}...") # Truncate for readability
            elif result.get("status") == "ignored":
                print(f"   [Smart Trigger] Ignored: {result.get('message')}")
            else:
                print(f"   [RAG] Status: {result.get('status')} - {result.get('message')}")
        
        print("-" * 40)
        # await asyncio.sleep(1) # Optional delay

if __name__ == "__main__":
    asyncio.run(simulate())
