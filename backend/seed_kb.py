import asyncio
import os
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

# Sample Data matching the Demo Script
documents = [
    {
        "content": "High-Yield Savings Plan (Tier 1): This plan offers an annualized return of 8-10%. It is principal-protected. Liquidity Terms: Partial withdrawals are allowed after 3 months with a nominal fee of 1%. Full penalty-free withdrawals are available after 1 year. Interest is compounded quarterly.",
        "metadata": {"name": "Product Sheet - High Yield Savings", "category": "Savings"}
    },
    {
        "content": "Market Volatility Protection: All our Tier 1 savings plans are 100% principal-protected. Even if the market dips, your initial investment remains secure. This is backed by our sovereign guarantee fund.",
        "metadata": {"name": "Risk Policy", "category": "Safety"}
    },
    {
        "content": "Account Opening Process: To open an account, the client needs to provide PAN card, Aadhar card, and a cancelled cheque. The process takes 24-48 hours.",
        "metadata": {"name": "Onboarding Guide", "category": "Operations"}
    }
]

async def seed():
    print("Seeding Knowledge Base...")
    
    for doc in documents:
        print(f"Embedding document: {doc['metadata']['name']}...")
        # Generate Embedding
        vector = embeddings.embed_query(doc['content'])
        
        # Insert into Supabase
        data = {
            "content": doc['content'],
            "metadata": doc['metadata'],
            "embedding": vector
        }
        
        try:
            supabase.table("knowledge_base").insert(data).execute()
            print(f"Inserted: {doc['metadata']['name']}")
        except Exception as e:
            print(f"Error inserting {doc['metadata']['name']}: {e}")

    print("Seeding Complete!")

if __name__ == "__main__":
    asyncio.run(seed())
