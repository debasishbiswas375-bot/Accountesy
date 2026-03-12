import os
from supabase import create_client

# Initialize Supabase Admin Client
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_SERVICE_ROLE_KEY") # Use Service Role for Admin tasks
supabase = create_client(url, key)

def get_all_users_summary():
    """
    Fetches the main list for the Admin Panel.
    Joins 'users' with 'plans' to show who is on Free/Pro.
    """
    try:
        # Fetching user details and their credit balances
        response = supabase.table("users").select("id, email, credits, role").execute()
        return response.data
    except Exception as e:
        print(f"Admin Fetch Error: {e}")
        return []

def update_user_credits(user_id, amount, action="add"):
    """
    Manually adjusts a user's credit balance.
    Action can be 'add' or 'set'.
    """
    try:
        if action == "add":
            # First get current balance
            current = supabase.table("users").select("credits").eq("id", user_id).single().execute()
            new_balance = float(current.data['credits']) + float(amount)
        else:
            new_balance = float(amount)

        # Update the database
        supabase.table("users").update({"credits": new_balance}).eq("id", user_id).execute()
        
        # Log the action in 'user_logs'
        supabase.table("user_logs").insert({
            "user_id": user_id,
            "action": "ADMIN_CREDIT_UPDATE",
            "details": f"Added {amount} credits. New balance: {new_balance}"
        }).execute()
        
        return True
    except Exception as e:
        print(f"Credit Update Error: {e}")
        return False

def get_system_stats():
    """
    Calculates total revenue and queue size for the Admin Dashboard.
    """
    # Total vouchers from conversion_history
    history = supabase.table("conversion_history").select("credits_used").execute()
    total_rev = sum([row['credits_used'] for row in history.data])
    
    # Active queue items
    queue = supabase.table("conversion_queue").select("id", count="exact").execute()
    
    return {
        "total_revenue": total_rev,
        "queue_count": queue.count or 0
    }
