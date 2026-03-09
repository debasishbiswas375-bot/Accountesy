from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from fastapi import Depends

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/", response_class=HTMLResponse)
async def landing(request: Request, db: Session = Depends(get_db)):
    plans = db.execute("SELECT * FROM plans").fetchall()
    return templates.TemplateResponse(
        "landing.html",
        {
            "request": request,
            "plans": plans
        }
    )


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/forgot", response_class=HTMLResponse)
async def forgot_page(request: Request):
    return templates.TemplateResponse("forgot.html", {"request": request})


@router.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/workspace", response_class=HTMLResponse)
async def workspace_page(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})


@router.get("/history", response_class=HTMLResponse)
async def history_page(request: Request):
    return templates.TemplateResponse("history.html", {"request": request})


@router.get("/features", response_class=HTMLResponse)
async def features_page(request: Request):
    return templates.TemplateResponse("features.html", {"request": request})


@router.get("/pricing", response_class=HTMLResponse)
async def pricing_page(request: Request, db: Session = Depends(get_db)):
    plans = db.execute("SELECT * FROM plans").fetchall()

    return templates.TemplateResponse(
        "pricing.html",
        {
            "request": request,
            "plans": plans
        }
    )
