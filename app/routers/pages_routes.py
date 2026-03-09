from fastapi import APIRouter,Request
from fastapi.templating import Jinja2Templates

router=APIRouter()
templates=Jinja2Templates(directory="app/templates")

@router.get("/")
def landing(request:Request):
 return templates.TemplateResponse("landing.html",{"request":request})

@router.get("/login")
def login_page(request:Request):
 return templates.TemplateResponse("login.html",{"request":request})

@router.get("/register")
def register_page(request:Request):
 return templates.TemplateResponse("register.html",{"request":request})

@router.get("/forgot")
def forgot_page(request:Request):
 return templates.TemplateResponse("forgot.html",{"request":request})
