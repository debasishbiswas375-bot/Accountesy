import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.database import supabase

router = APIRouter(prefix="/history", tags=["History"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
user_templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

@router.get("/")
def show_conversion_history(request: Request):
    if not supabase:
        return {"error": "Database not connected"}
    
    # Pull history ordered by most recent first
    res = supabase.table("conversion_history").select("*").order("created_at", desc=True).execute()
    
    return user_templates.TemplateResponse(
        "history.html", 
        {"request": request, "history": res.data}
    )
