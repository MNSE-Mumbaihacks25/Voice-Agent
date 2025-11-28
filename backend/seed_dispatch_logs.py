import os
import asyncio
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    print("Error: SUPABASE_URL or SUPABASE_KEY not found in environment.")
    exit(1)

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

async def seed_dispatch_logs():
    print("Seeding ai_dispatch_logs...")

    # Fetch existing agents to ensure valid foreign keys/mappings
    agents_response = supabase.table("agents").select("agent_id").execute()
    agents = agents_response.data
    
    if not agents:
        print("No agents found. Please seed agents first.")
        return

    print(f"Found {len(agents)} agents: {[a['agent_id'] for a in agents]}")

    # Sample data templates
    lead_templates = [
        {
            "lead_name": "Amit Kumar",
            "lead_persona": "Conservative Investor, Age 35",
            "top_candidate": "HDFC Top 100 Fund",
            "math_score": 95,
            "second_score": 88,
            "is_override": False,
            "reasoning": "High match with risk appetite and long-term goals. Client prefers stable large-cap funds.",
            "admin_corrected": False
        },
        {
            "lead_name": "Sneha Gupta",
            "lead_persona": "Aggressive Trader, Age 28",
            "top_candidate": "Nifty 50 Index Fund",
            "math_score": 82,
            "second_score": 75,
            "is_override": False,
            "reasoning": "Good fit for SIP capacity, but slightly lower risk tolerance than required for mid-caps.",
            "admin_corrected": False
        },
        {
            "lead_name": "Vikram Singh",
            "lead_persona": "High Net Worth Individual, Age 45",
            "top_candidate": "Reliance Industries Stock",
            "math_score": 98,
            "second_score": 90,
            "is_override": True,
            "reasoning": "Direct equity exposure requested. Strong balance sheet alignment.",
            "admin_corrected": False
        },
        {
            "lead_name": "Anjali Desai",
            "lead_persona": "Young Professional, Age 24",
            "top_candidate": "Axis Bluechip Fund",
            "math_score": 88,
            "second_score": 85,
            "is_override": False,
            "reasoning": "Starting early with SIPs. Bluechip provides safety with growth.",
            "admin_corrected": False
        }
    ]

    logs = []
    # Distribute leads among agents
    for i, template in enumerate(lead_templates):
        agent = agents[i % len(agents)] # Round-robin assignment
        log = template.copy()
        log["assigned_agent"] = agent["agent_id"]
        logs.append(log)

    for log in logs:
        try:
            # Check if lead already exists to avoid duplicates (optional, based on name)
            # For now, just insert.
            data = supabase.table("ai_dispatch_logs").insert(log).execute()
            print(f"Inserted log for {log['lead_name']} assigned to {log['assigned_agent']}")
        except Exception as e:
            print(f"Error inserting {log['lead_name']}: {e}")

    print("Seeding complete.")

if __name__ == "__main__":
    asyncio.run(seed_dispatch_logs())
