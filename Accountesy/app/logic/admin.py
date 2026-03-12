import os
from database import supabase_admin # Uses Service Role from Render ENV

def get_all_users():
    """Fetches all users to monitor credit balances"""
    try:
        response = supabase_admin.table("users").select("*").execute()
        return response.data
    except Exception as e:
        print(f"Error fetching users: {e}")
        return []

def add_user_credits(user_id, amount):
    """Manually add credits for offline payments"""
    try:
        # Get current balance
        res = supabase_admin.table("users").select("credits").eq("id", user_id).single().execute()
        new_total = float(res.data['credits']) + float(amount)
        
        # Update balance
        supabase_admin.table("users").update({"credits": new_total}).eq("id", user_id).execute()
        return True
    except Exception as e:
        print(f"Credit update failed: {e}")
        return False
