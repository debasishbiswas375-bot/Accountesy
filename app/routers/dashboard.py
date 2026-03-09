from fastapi import APIRouter, Request, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])
templates = Jinja2Templates(directory="templates")

@router.get("/", response_class=HTMLResponse)
async def read_dashboard(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        # If they aren't logged in, send them to login
        return RedirectResponse(url="/auth/login", status_code=303)
        
    try:
        db = get_db()
        user_auth = db.auth.get_user(token).user
        user_data_res = db.table("users").select("*").eq("id", user_auth.id).execute()
        
        user_db = user_data_res.data[0] if user_data_res.data else {}
        
        return templates.TemplateResponse("dashboard.html", {
            "request": request,
            "plan": user_db.get("plan_id", "Free"),
            "credits": user_db.get("credits", 0),
            "conversions": 0,
            "email": user_auth.email
        })
    except Exception as e:
        res = RedirectResponse(url="/auth/login", status_code=303)
        res.delete_cookie("access_token")
        return res
