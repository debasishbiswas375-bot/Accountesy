from fastapi import Request, HTTPException
from supabase import create_client

# These should be in your Render Environment Variables
url = os.environ.get("SUPABASE_URL")
key = os.environ.get("SUPABASE_KEY")
supabase = create_client(url, key)

async def get_current_user(request: Request):
    """
    Checks if the user is logged in via Supabase.
    Ensures email is verified before allowing conversion.
    """
    session = request.cookies.get("session")
    if not session:
        return None
    
    user = supabase.auth.get_user(session)
    if not user:
        return None
        
    # Safeguard: Check if email is verified
    if not user.user.email_confirmed_at:
        raise HTTPException(status_code=403, detail="Please verify your email first.")
        
    return user.user
