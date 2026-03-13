from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.database import supabase

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/admin")
def admin_panel(request: Request):

    users = supabase.table("users").select("*").execute()

    return templates.TemplateResponse(
        "admin.html",
        {
            "request": request,
            "users": users.data
        }
    )
