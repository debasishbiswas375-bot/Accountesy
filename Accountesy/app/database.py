import os
from supabase import create_client, Client

# These keys MUST be added to your Render Environment Variables
url: str = os.environ.get("SUPABASE_URL")
key: str = os.environ.get("SUPABASE_KEY") # Use anon key
service_key: str = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # For admin bypass

# Standard connection
supabase: Client = create_client(url, key)

# Admin connection (Used in admin.py logic)
supabase_admin: Client = create_client(url, service_key)
