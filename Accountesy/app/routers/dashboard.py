def get_user_stats(user_id, supabase_client):
    """
    Fetches stats from:
    1. 'users' table (credits)
    2. 'conversion_history' (count)
    3. 'ai_memory' (learned patterns)
    """
    user_data = supabase_client.table("users").select("credits").eq("id", user_id).single().execute()
    history_count = supabase_client.table("conversion_history").select("id", count="exact").eq("user_id", user_id).execute()
    ai_count = supabase_client.table("ai_memory").select("id", count="exact").eq("user_id", user_id).execute()
    
    return {
        "credits": user_data.data['credits'],
        "total_vouchers": history_count.count or 0,
        "patterns": ai_count.count or 0
    }
