from fastapi import APIRouter, Request, Form, HTTPException, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from app.database import get_db

router = APIRouter(prefix="/auth", tags=["Authentication"])
templates = Jinja2Templates(directory="templates")

@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@router.post("/login")
async def process_login(request: Request, email: str = Form(...), password: str = Form(...)):
    db = get_db()
    try:
        # 1. Ask Supabase to verify the user
        response = db.auth.sign_in_with_password({"email": email, "password": password})
        session = response.session
        
        # 2. If successful, send them to the dashboard
        redirect = RedirectResponse(url="/", status_code=303)
        
        # 3. Store the secure login token in their browser cookies
        redirect.set_cookie(
            key="access_token", 
            value=session.access_token, 
            httponly=True,  # Prevents JavaScript hackers from stealing the token
            max_age=session.expires_in
        )
        return redirect
    except Exception as e:
        # If login fails, reload the page with an error
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid email or password."})

@router.get("/register", response_class=HTMLResponse)
async def register_page(request: Request):
    return templates.TemplateResponse("register.html", {"request": request})

@router.post("/register")
async def process_register(request: Request, email: str = Form(...), password: str = Form(...)):
    db = get_db()
    try:
        # 1. Create the user in Supabase Auth
        response = db.auth.sign_up({"email": email, "password": password})
        
        # 2. Redirect to login page with a success message
        return templates.TemplateResponse("login.html", {
            "request": request, 
            "success": "Account created! Please log in."
        })
    except Exception as e:
        return templates.TemplateResponse("register.html", {"request": request, "error": str(e)})

@router.get("/logout")
async def logout():
    # Delete the cookie and send them back to the login page
    redirect = RedirectResponse(url="/auth/login", status_code=303)
    redirect.delete_cookie("access_token")
    return redirect
