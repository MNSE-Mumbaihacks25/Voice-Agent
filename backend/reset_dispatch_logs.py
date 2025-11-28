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

# Data provided by user
csv_data = """
342bf97f-8d9b-4a6c-a005-48faa92d2efd,Anil Reddy,Gig Worker (Tamil),Amit Nair,Amit Nair,78,78,false,Assigned to Amit Nair due to strong language match with the lead's preference (Tamil).,false,2025-11-28 22:36:16.767308+00
3aebca5c-8f5e-4304-840e-a1b9af1690c4,Divya Nair,Salaried (English),Ganesh Verma,Ganesh Verma,79,79,false,"Ganesh Verma was assigned due to his English language proficiency, which matches the lead's requirement, and his manageable current lead load of 1, which is not exceeding the threshold.",false,2025-11-28 22:35:49.594833+00
65fd9dd9-cd52-4f88-807e-281c1cd28ca6,Varun Singh,Salaried (Marathi),Anjali Joshi,Anjali Joshi,77,77,false,"Anjali Joshi speaks Marathi, matching the lead's preferred language, and her current lead load is not excessive.",false,2025-11-28 22:36:50.82169+00
6ad454b0-0365-499d-8b01-dad5788acf54,Riya Kulkarni,Gig Worker (English),Raju Singh,Raju Singh,83,83,false,"Raju Singh is the top candidate and speaks English, which matches the lead's language preference. His current load is within the acceptable limit.",false,2025-11-28 22:34:34.338029+00
7612052a-78b3-40e5-81de-0d8e6f7fd756,Aditi Kulkarni,Salaried (English),Deepak Singh,Deepak Singh,78,78,false,"Deepak Singh is assigned as he speaks English, matching the lead's language preference, and has a manageable current lead load.",false,2025-11-28 22:36:25.656603+00
789eb8fc-de7c-462c-a4c9-de1aa49dad39,Anil Kale,Salaried (Tamil),Anita Joshi,Anita Joshi,77,77,false,"Anita Joshi speaks Tamil, matching the lead's language requirement, and has a manageable lead load.",false,2025-11-28 22:36:58.714854+00
88380013-370e-4257-a89e-21251f0448b1,Ramesh Reddy,Salaried (English),Sneha Verma,Sneha Verma,82,82,false,"Sneha Verma is assigned due to her proficiency in English, matching the lead's language requirement, and her current manageable lead load.",false,2025-11-28 22:35:07.722547+00
8e7b377c-0c7a-449b-a52b-7226fff75951,Riya Deshmukh,Salaried (Marathi),Karan Sharma,Karan Sharma,81,79,false,"Karan Sharma is assigned due to his strong language match (Marathi) with the lead and his current low lead load, ensuring dedicated service.",false,2025-11-28 22:35:28.761991+00
8f843f5c-ef5b-48ae-bdf0-87b4e45b4ad4,Kavita Verma,Retired (English),Aditi Sharma,Aditi Sharma,83,83,false,"Aditi Sharma is assigned as she proficiently speaks English, matching the lead's language requirement, and her current lead load is optimal.",false,2025-11-28 22:34:16.981815+00
9b3034db-93f8-4c60-bff0-4922c94dd154,Deepak Deshmukh,Salaried (English),Sunil Sharma,Sunil Sharma,79,78,false,"Sunil Sharma is assigned due to his strong English language proficiency, which directly matches the lead's language requirement, and his current manageable lead load.",false,2025-11-28 22:36:02.165716+00
a0da4aef-38a2-44a1-a8bc-0c6fb99f8c93,Priya Kale,Retired (Marathi),Aditi Singh,Aditi Singh,77,76,false,"Aditi Singh is the top-scoring candidate with a strong language match (Marathi), ensuring effective communication with the lead. Her current lead load is also optimal.",false,2025-11-28 22:37:06.810926+00
b3ebe140-2fa6-4a0b-88b9-be406904de35,Anil Deshmukh,Salaried (Marathi),Kavita Das,Kavita Das,78,77,false,"Kavita Das is assigned due to her proficiency in Marathi, directly matching the lead's language preference, and her current manageable lead load.",false,2025-11-28 22:36:34.727389+00
e21637fd-c75f-4f53-8d83-1f84199fde74,Anil Nair,Business (English),Neha Sharma,Neha Sharma,79,79,false,"Neha Sharma is assigned due to her excellent language match (English) with the lead, ensuring effective communication. Her current lead load is also suitable.",false,2025-11-28 22:35:38.363079+00
e37ccbc4-dcd8-4d91-ae42-001e1eb32b39,Meena Shinde,Salaried (Tamil),Aditi Deshmukh,Aditi Deshmukh,83,82,false,Assigned based on strong language match (Tamil) for effective communication with the lead and optimal lead load.,false,2025-11-28 22:34:54.320016+00
ece19892-bc5c-4ab2-850c-ec34e339427c,Ganesh Kulkarni,Salaried (English),Ganesh Kale,Ganesh Kale,82,81,false,"Ganesh Kale is assigned as he speaks English, matching the lead's language requirement, and has a manageable current lead load.",false,2025-11-28 22:35:16.980728+00
"""

async def reset_dispatch_logs():
    print("Resetting ai_dispatch_logs...")
    
    # 1. Truncate table (delete all rows)
    try:
        # Note: Supabase-py doesn't have a direct truncate, so we delete all.
        # Assuming 'id' is a column we can filter on, or we can use a condition that matches all.
        # Or we can just delete where id is not null.
        # But wait, we need to be careful.
        # Let's try to delete all.
        supabase.table("ai_dispatch_logs").delete().neq("lead_name", "PLACEHOLDER_TO_MATCH_ALL").execute() 
        # Actually .neq("id", "00000000-0000-0000-0000-000000000000") might work if UUID.
        # Or just loop and delete if needed, but that's slow.
        # Let's assume we can just insert and ignore duplicates? No, we want to remove old ones.
        
        # Better approach: Just insert the new ones. If we want to clear old ones, we might need a separate step.
        # Let's try to delete everything first.
        # A trick to delete all rows: .neq("lead_name", "NonExistentName") will delete nothing.
        # .gt("created_at", "1970-01-01") should match all.
        supabase.table("ai_dispatch_logs").delete().gt("created_at", "1970-01-01").execute()
        print("Cleared existing logs.")
    except Exception as e:
        print(f"Error clearing logs: {e}")

    lines = csv_data.strip().split('\n')
    for line in lines:
        parts = line.split(',')
        if len(parts) < 5:
            continue
            
        # Parse (rough)
        # id,lead_name,lead_persona,top_candidate,assigned_agent,math_score,second_score,is_override,reasoning,admin_corrected,created_at
        log = {
            "id": parts[0],
            "lead_name": parts[1],
            "lead_persona": parts[2],
            "top_candidate": parts[3],
            "assigned_agent": parts[4],
            "math_score": int(parts[5]),
            "second_score": int(parts[6]),
            "is_override": parts[7].lower() == 'true',
            "reasoning": parts[8].strip('"'), # Remove quotes if present
            "admin_corrected": parts[9].lower() == 'true',
            # "created_at": parts[10] # Let DB handle or use provided
        }
        
        try:
            supabase.table("ai_dispatch_logs").insert(log).execute()
            print(f"Inserted log for {log['lead_name']}")
        except Exception as e:
            print(f"Error inserting {log['lead_name']}: {e}")

    print("Reset complete.")

if __name__ == "__main__":
    asyncio.run(reset_dispatch_logs())
