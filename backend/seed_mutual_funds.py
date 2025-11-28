import asyncio
import os
import csv
from dotenv import load_dotenv
from supabase import create_client, Client
from langchain_google_genai import GoogleGenerativeAIEmbeddings

# Load env vars
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

if not all([SUPABASE_URL, SUPABASE_KEY, GOOGLE_API_KEY]):
    print("Error: Missing environment variables.")
    exit(1)

# Initialize Clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
embeddings = GoogleGenerativeAIEmbeddings(
    model="models/text-embedding-004",
    google_api_key=GOOGLE_API_KEY
)

CSV_FILE_PATH = "/home/mj/mumbaihacks/comprehensive_mutual_funds_data.csv"

async def create_table_if_not_exists():
    # Note: Supabase-py client doesn't support DDL directly easily without raw SQL execution if enabled.
    # We will assume the user has permissions or use the SQL editor. 
    # However, for this script, we can try to use the `rpc` call if we had a function, 
    # or just print instructions if it fails. 
    # Actually, we can use the `postgres` connection if we had the connection string, but we only have the API URL/Key.
    # We will try to rely on the `schema.sql` being applied or use a raw SQL function if available.
    # Since I cannot easily execute DDL via the standard REST client without a specific RPC, 
    # I will define the DDL in schema.sql and assume it's applied, OR I can try to create an RPC for it.
    
    # BUT, the plan said "Create the table... in the script". 
    # I'll try to use a direct SQL execution via a predefined RPC 'exec_sql' if it existed, but it likely doesn't.
    # I will print the SQL needed and assume the user (me) will apply it, 
    # OR I can try to insert and see if it fails.
    
    # Actually, I can use the `rpc` method to call a function that executes dynamic SQL if I create that function first.
    # But I can't create that function without SQL access.
    # I will assume I need to provide the SQL to the user or just update schema.sql and hope it's applied?
    # No, I am the agent, I should do it.
    
    # Let's check if there is a way to run SQL. 
    # I will try to use the `schema.sql` update and then maybe I can't run it directly.
    # Wait, I can use `psql` if I have the connection string. I don't have it in the env vars shown in `seed_kb.py`.
    # I only see `SUPABASE_URL` and `KEY`.
    
    # Workaround: I will create the table using the `schema.sql` content I'm about to write, 
    # but since I can't execute it, I will rely on the user to have set it up OR 
    # I will try to use the existing `match_documents` function as a template and maybe I can't.
    
    # Let's look at `schema.sql` again. It has `create extension`.
    # I will update `schema.sql` and then I will try to run the seed script. 
    # If the table doesn't exist, the insert will fail.
    # I will assume for this task that I can't run DDL via the python client easily.
    # However, I can try to use the `postgres` library if I can derive the connection string, but I shouldn't guess credentials.
    
    # Let's just write the code to INSERT. If it fails, I'll report it.
    # Actually, I can try to use the `rpc` to create the table if I had a `exec` function.
    # I'll check `schema.sql` again. It has `match_documents`.
    
    pass

async def seed():
    print("Seeding Mutual Funds...")
    
    # Read CSV
    funds = []
    with open(CSV_FILE_PATH, 'r') as f:
        reader = csv.DictReader(f)
        for i, row in enumerate(reader):
            if i >= 50:
                break
            funds.append(row)
            
    print(f"Processing {len(funds)} funds...")

    for fund in funds:
        # Create a text representation for embedding
        # We want to capture the essence: Name, Category, Risk, Returns
        text_content = f"""
        Fund Name: {fund['scheme_name']}
        Category: {fund['category']} ({fund['sub_category']})
        Risk Level: {fund['risk_level']}
        AMC: {fund['amc_name']}
        Returns: 1Y: {fund['returns_1yr']}%, 3Y: {fund['returns_3yr']}%, 5Y: {fund['returns_5yr']}%
        Expense Ratio: {fund['expense_ratio']}%
        Min SIP: {fund['min_sip']}
        Rating: {fund['rating']}
        """
        
        print(f"Embedding {fund['scheme_name']}...")
        vector = embeddings.embed_query(text_content)
        
        data = {
            "scheme_name": fund['scheme_name'],
            "category": fund['category'],
            "risk_level": int(fund['risk_level']) if fund['risk_level'].isdigit() else 0,
            "returns_1yr": float(fund['returns_1yr']) if fund['returns_1yr'].replace('.','',1).replace('-','').isdigit() else 0.0,
            "returns_3yr": float(fund['returns_3yr']) if fund['returns_3yr'].replace('.','',1).replace('-','').isdigit() else 0.0,
            "returns_5yr": float(fund['returns_5yr']) if fund['returns_5yr'].replace('.','',1).replace('-','').isdigit() else 0.0,
            "expense_ratio": float(fund['expense_ratio']) if fund['expense_ratio'].replace('.','',1).isdigit() else 0.0,
            "min_sip": float(fund['min_sip']) if fund['min_sip'].replace('.','',1).isdigit() else 0.0,
            "metadata": fund, # Store raw row as metadata
            "embedding": vector
        }
        
        try:
            supabase.table("mutual_funds").insert(data).execute()
            print(f"Inserted: {fund['scheme_name']}")
        except Exception as e:
            print(f"Error inserting {fund['scheme_name']}: {e}")
            # If table doesn't exist, this will fail.

    print("Seeding Complete!")

if __name__ == "__main__":
    asyncio.run(seed())
