from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

@router.get("/dashboard")
def dashboard(request: Request):

    user = {
        "name":"Demo User",
        "credits":25.5,
        "vouchers":255,
        "plan":"Starter",
        "expiry":"2026-03-30"
    }

    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request,"user":user}
    )
