import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def debug_mapping():
    print("--- Debugging Agent Mapping ---")
    
    # 1. Check Agent 100
    agent_id = "agt_100" # Assuming this is the ID user is testing with
    print(f"\nFetching Agent: {agent_id}")
    agent_res = supabase.table("agents").select("*").eq("agent_id", agent_id).execute()
    print(f"Agent Data: {agent_res.data}")
    
    if agent_res.data:
        agent_name = agent_res.data[0].get("name")
        print(f"Resolved Name: '{agent_name}'")
        
        # 2. Check Logs for this Name
        print(f"\nFetching Logs for Assigned Agent: '{agent_name}'")
        logs_res = supabase.table("ai_dispatch_logs").select("*").eq("assigned_agent", agent_name).execute()
        print(f"Logs Found: {len(logs_res.data)}")
        if logs_res.data:
            print(f"First Log: {logs_res.data[0]}")
    else:
        print("Agent not found.")

    # 3. List all unique assigned_agents in logs
    print("\n--- All Assigned Agents in Logs ---")
    all_logs = supabase.table("ai_dispatch_logs").select("assigned_agent").execute()
    unique_agents = set(log["assigned_agent"] for log in all_logs.data)
    print(f"Unique Agents in Logs: {unique_agents}")

    # 4. List all agents
    print("\n--- All Agents in Agents Table ---")
    all_agents = supabase.table("agents").select("agent_id, name").execute()
    for a in all_agents.data:
        print(f"ID: {a['agent_id']}, Name: {a['name']}")

if __name__ == "__main__":
    asyncio.run(debug_mapping())
