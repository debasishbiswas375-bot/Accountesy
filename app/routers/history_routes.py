import os
from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.database import supabase

router = APIRouter(prefix="/history", tags=["History"])

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
user_templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))


# =========================================
# 🔹 HISTORY PAGE
# =========================================
@router.get("/")
def show_conversion_history(request: Request):

    if not supabase:
        return {"error": "Database not connected"}

    user = request.cookies.get("user")

    # 👤 Guest user
    if not user:
        return user_templates.TemplateResponse(
            "history.html",
            {
                "request": request,
                "history": [],
                "guest": True
            }
        )

    # 👤 Logged user
    res = supabase.table("conversion_history").select("*").execute()

    return user_templates.TemplateResponse(
        "history.html",
        {
            "request": request,
            "history": res.data,
            "guest": False
        }
    )
