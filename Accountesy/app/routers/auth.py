from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from app.database import supabase

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


@router.get("/login")
def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@router.get("/register")
def register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})
