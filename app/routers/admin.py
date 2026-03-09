from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from app.database import get_db

router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(request: Request):
    db = get_db()
    # Fetch all users and plans to pass to the template
    # users = db.table("users").select("*").execute()
    return templates.TemplateResponse("admin.html", {"request": request})
