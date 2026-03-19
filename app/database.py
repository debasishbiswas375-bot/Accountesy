import os
from supabase import create_client, Client

# These variables are pulled safely from your Render "Environment" tab
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

try:
    if SUPABASE_URL and SUPABASE_KEY:
        supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Supabase Connection: Active")
    else:
        print("❌ Supabase Connection: Keys missing in Environment")
        supabase = None
except Exception as e:
    print(f"❌ Supabase Connection Error: {e}")
    supabase = None
