from supabase import create_client
import os

SUPABASE_URL = os.getenv("DATABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # 👈 keep anon key for now

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
