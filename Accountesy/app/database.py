import os
from supabase import create_client, Client

# Automatically extract Supabase URL from your existing Postgres string
db_url = os.environ.get("DATABASE_URL", "")

if "supabase.com" in db_url:
    # Extracts the unique project ID from the database URL
    project_id = db_url.split('@')[-1].split('.')[0].replace("aws-0-", "")
    generated_url = f"https://{project_id}.supabase.co"
else:
    generated_url = os.environ.get("SUPABASE_URL")

# Uses your SECRET_KEY for the API connection
api_key = os.environ.get("SECRET_KEY")

if not generated_url or not api_key:
    print("❌ ERROR: Missing SUPABASE_URL or SECRET_KEY in Render ENV")

supabase: Client = create_client(generated_url, api_key)
supabase_admin: Client = create_client(generated_url, api_key)
