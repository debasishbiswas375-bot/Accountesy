import os
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import supabase # Import your live database connection

router = APIRouter(prefix="/admin", tags=["Admin"])

# Point STRICTLY to the isolated app/admin folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
admin_templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "admin"))

# --- SECURE LOGIN ---
@router.get("/login")
def admin_login_page(request: Request):
    return admin_templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/login")
def process_admin_login(username: str = Form(...), password: str = Form(...)):
    # Pulling directly from your Render Environment Variables
    secure_username = os.getenv("ADMIN_USERNAME")
    secure_password = os.getenv("ADMIN_PASSWORD")
    
    if username == secure_username and password == secure_password:
        return RedirectResponse(url="/admin/", status_code=302)
    return {"error": "Invalid Admin Credentials"}

# --- LIVE DASHBOARD ---
@router.get("/")
def admin_dashboard(request: Request):
    live_users = []
    if supabase:
        try:
            # Fetch users from Supabase table
            response = supabase.table("users").select("id, name, email, plan").execute()
            live_users = response.data
        except Exception as e:
            print(f"Supabase Data Error: {e}")

    return admin_templates.TemplateResponse(
        "admin_dashboard.html", 
        {"request": request, "users": live_users}
    )

# --- UPDATE USER PLAN ---
@router.post("/update-user")
def update_user_plan(user_id: int = Form(...), new_plan: str = Form(...)):
    if supabase:
        try:
            # Save the plan change directly to Supabase
            supabase.table("users").update({"plan": new_plan}).eq("id", user_id).execute()
        except Exception as e:
            print(f"Supabase Update Error: {e}")

    return RedirectResponse(url="/admin/", status_code=302)
