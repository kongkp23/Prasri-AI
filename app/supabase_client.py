import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

url: str = os.environ.get("SUPABASE_URL", "")
key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "")

supabase = None
if url and key:
    try:
        supabase = create_client(url, key)
    except Exception as e:
        print(f"Error initializing Supabase client: {e}")
else:
    print("Warning: SUPABASE_URL and/or SUPABASE_SERVICE_ROLE_KEY are not set.")

def get_supabase():
    if not supabase:
        raise ValueError("Supabase client is not initialized. Check Vercel Environment Variables.")
    return supabase
