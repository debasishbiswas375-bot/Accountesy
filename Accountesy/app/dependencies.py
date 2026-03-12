import os
from fastapi import Request, HTTPException
from database import supabase #

async def get_current_user(request: Request):
    """Verifies session and checks Supabase Email Verification status."""
    session = request.cookies.get("session")
    if not session:
        raise HTTPException(status_code=401, detail="Please login first.")
    
    user_res = supabase.auth.get_user(session)
    if not user_res.user:
        raise HTTPException(status_code=401, detail="Invalid Session")
        
    # Check for Supabase Verified Email
    if not user_res.user.email_confirmed_at:
        raise HTTPException(status_code=403, detail="Email not verified.")
        
    return user_res.user

async def check_credit_eligibility(user_id: str, voucher_count: int):
    """Rule: 0.1 Credits per Voucher"""
    required = round(voucher_count * 0.1, 2)
    
    # Check 'users' table balance
    res = supabase.table("users").select("credits").eq("id", user_id).single().execute()
    balance = float(res.data.get('credits', 0))
    
    if balance < required:
        raise HTTPException(status_code=402, detail=f"Insufficient Credits. Need {required}.")
    
    return True
