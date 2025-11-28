import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv
import json

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def verify_storage():
    lead_id = "e21637fd-c75f-4f53-8d83-1f84199fde74"
    print(f"--- Verifying Storage for Lead ID: {lead_id} ---")
    
    # 1. Check ai_dispatch_logs
    print("\n1. Checking ai_dispatch_logs...")
    log_res = supabase.table("ai_dispatch_logs").select("*").eq("id", lead_id).execute()
    if log_res.data:
        log = log_res.data[0]
        print(f"Lead Name: {log.get('lead_name')}")
        print(f"Assigned Agent: {log.get('assigned_agent')}")
        
        # Check if chat_history column exists and has data
        if "chat_history" in log:
            history = log["chat_history"]
            print(f"chat_history in ai_dispatch_logs: {type(history)}")
            if isinstance(history, list):
                print(f"Count: {len(history)}")
            else:
                print(f"Content: {history}")
        else:
            print("chat_history column NOT found in ai_dispatch_logs")
            
        lead_name = log.get("lead_name")
        
        # 2. Check investors
        print(f"\n2. Checking investors for Name: '{lead_name}'...")
        inv_res = supabase.table("investors").select("*").eq("name", lead_name).execute()
        if inv_res.data:
            inv = inv_res.data[0]
            print(f"Investor ID: {inv.get('investor_id')}")
            
            if "chat_history" in inv:
                history = inv["chat_history"]
                print(f"chat_history in investors: {type(history)}")
                if isinstance(history, list):
                    print(f"Count: {len(history)}")
                    if len(history) > 0:
                        print("Sample Entry keys:", history[0].keys())
                else:
                    print(f"Content: {history}")
            else:
                print("chat_history column NOT found in investors")
        else:
            print(f"Investor not found with name: {lead_name}")
            
    else:
        print("Lead not found in ai_dispatch_logs")

if __name__ == "__main__":
    asyncio.run(verify_storage())
