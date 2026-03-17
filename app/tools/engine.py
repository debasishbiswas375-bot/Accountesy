from app.database import supabase

def smart_classify(df, user_id: str):
    """The Brain: Checks ai_memory table for learned patterns."""
    df['ledger_name'] = "Suspense Account"
    
    try:
        # 1. Fetch learned patterns for this specific user
        res = supabase.table("ai_memory").select("narration_pattern, suggested_ledger").eq("user_id", user_id).execute()
        memory_map = {item['narration_pattern']: item['suggested_ledger'] for item in res.data}
        
        # 2. Apply Memory (Exact Match)
        for idx, row in df.iterrows():
            clean_desc = str(row['description']).lower().strip()
            if clean_desc in memory_map:
                df.at[idx, 'ledger_name'] = memory_map[clean_desc]
                
        # 3. Apply General Keyword Rules for remaining 'Suspense'
        general_rules = {
            "Staff Welfare": ["zomato", "swiggy", "tea", "coffee"],
            "Bank Charges": ["chgs", "gst", "processing fee", "maintenance"],
            "Fuel": ["petrol", "hpcl", "indian oil", "shell"]
        }
        
        for ledger, keywords in general_rules.items():
            for kw in keywords:
                mask = (df['description'].str.contains(kw, case=False, na=False)) & (df['ledger_name'] == "Suspense Account")
                df.loc[mask, 'ledger_name'] = ledger
    except Exception as e:
        print(f"Engine Error: {e}")
        
    return df

def learn_new_pattern(user_id: str, narration: str, ledger: str):
    """Saves user-corrected ledger back to ai_memory."""
    data = {
        "user_id": user_id,
        "narration_pattern": narration.lower().strip(),
        "suggested_ledger": ledger,
        "confidence_level": 100
    }
    supabase.table("ai_memory").upsert(data, on_conflict="user_id,narration_pattern").execute()
