from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import get_db

router = APIRouter(tags=["Dashboard"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    token = request.cookies.get("access_token")
    
    # 1. If no cookie exists, kick them back to the login page
    if not token:
        return RedirectResponse(url="/auth/login", status_code=303)
        
    try:
        db = get_db()
        # 2. Get the authenticated user from Supabase
        user_auth = db.auth.get_user(token).user
        
        # 3. Fetch their live credits and plan from the public.users table
        user_data_res = db.table("users").select("*").eq("id", user_auth.id).execute()
        
        if not user_data_res.data:
            # Fallback just in case the database row hasn't synced yet
            credits = 0
            plan_name = "Free"
        else:
            user_db = user_data_res.data[0]
            credits = user_db.get("credits", 0)
            # In a full system, you would do a SQL JOIN to get the text name of the plan_id
            plan_name = "Active Plan" 
            
        # 4. Count their total successful conversions from the history table
        history_res = db.table("conversion_history").select("id", count="exact").eq("user_id", user_auth.id).execute()
        conversions = history_res.count if history_res.count else 0

        # 5. Inject the live data into the Jinja2 HTML template
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "plan": plan_name,
            "credits": credits,
            "conversions": conversions,
            "email": user_auth.email
        })
        
    except Exception as e:
        # If the token expired or is fake, delete it and force a new login
        response = RedirectResponse(url="/auth/login", status_code=303)
        response.delete_cookie("access_token")
        return response
