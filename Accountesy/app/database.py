import os
from supabase import create_client, Client

db_url = os.environ.get("DATABASE_URL", "")
generated_url = None

# Extracts project ID from the postgres string
if "supabase.com" in db_url:
    try:
        project_id = db_url.split('@')[-1].split('.')[0].replace("aws-0-", "")
        generated_url = f"https://{project_id}.supabase.co"
    except Exception:
        generated_url = os.environ.get("SUPABASE_URL")
else:
    generated_url = os.environ.get("SUPABASE_URL")

api_key = os.environ.get("SECRET_KEY")

# Primary clients for the app
supabase: Client = create_client(generated_url, api_key)
supabase_admin: Client = create_client(generated_url, api_key)
