import os
from supabase import create_client, Client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("Supabase connection established successfully!")
    else:
        print("Warning: Supabase credentials not found in environment.")
        supabase = None
except Exception as e:
    print(f"Error initializing Supabase: {e}")
    supabase = None
