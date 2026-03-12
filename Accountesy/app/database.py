import os
from supabase import create_client, Client

# MAPPING TO YOUR EXISTING RENDER KEYS
# We extract the Project URL from your DATABASE_URL string automatically
db_url = os.environ.get("DATABASE_URL", "")

# Logic to extract 'xyz.supabase.co' from your postgres string
if "supabase.com" in db_url:
    # Your project ID is the first part of the host in the DATABASE_URL
    project_id = db_url.split('@')[-1].split('.')[0]
    generated_url = f"https://{project_id}.supabase.co"
else:
    # Fallback if the extraction fails
    generated_url = None

# Using SECRET_KEY as a stand-in for the API key if anon key isn't present
# Note: For full security, the 'anon' key is preferred, but this uses your existing setup
api_key = os.environ.get("SECRET_KEY")

if not generated_url or not api_key:
    print("❌ ERROR: Could not identify Supabase URL from existing DATABASE_URL!")

# Standard client for your app logic
supabase: Client = create_client(generated_url, api_key)

# Admin client for credit overrides
supabase_admin: Client = create_client(generated_url, api_key)
