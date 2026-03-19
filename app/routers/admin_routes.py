import os
from fastapi import APIRouter, Request, Form, Depends
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from app.database import supabase

router = APIRouter(prefix="/admin", tags=["Admin"])

# Pointing to the isolated admin folder
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
admin_templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "admin"))

@router.get("/login")
def admin_login_page(request: Request):
    return admin_templates.TemplateResponse("admin_login.html", {"request": request})

@router.post("/login")
def process_admin_login(username: str = Form(...), password: str = Form(...)):
    # Authenticates against Render Environment Variables
    if username == os.getenv("ADMIN_USERNAME") and password == os.getenv("ADMIN_PASSWORD"):
        response = RedirectResponse(url="/admin/", status_code=302)
        # In a real app, you'd set a secure cookie here
        return response
    return {"error": "Invalid Admin Credentials"}

@router.get("/")
def admin_dashboard(request: Request):
    if not supabase:
        return {"error": "Database connection failed"}
    
    # Fetch all users from Supabase to manage plans
    res = supabase.table("users").select("*").execute()
    return admin_templates.TemplateResponse(
        "admin_dashboard.html", 
        {"request": request, "users": res.data}
    )

@router.post("/update-user")
def update_user_plan(user_id: str = Form(...), new_plan: str = Form(...)):
    if supabase:
        # Update the specific user's plan in the DB
        supabase.table("users").update({"plan": new_plan}).eq("id", user_id).execute()
    return RedirectResponse(url="/admin/", status_code=302)
