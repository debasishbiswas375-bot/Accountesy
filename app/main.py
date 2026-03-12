from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
import threading

from .database import engine, SessionLocal, Base
from .models import User, Plan
from .auth import get_password_hash

# --------------------------------------------------
# App Init
# --------------------------------------------------

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

STATIC_DIR = os.path.join(BASE_DIR, "static")
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")

app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

# --------------------------------------------------
# Create Tables (lightweight)
# --------------------------------------------------

Base.metadata.create_all(bind=engine)

# --------------------------------------------------
# Non-blocking Initial Data Setup
# --------------------------------------------------

def init_data_background():
    db = SessionLocal()
    try:
        # Create Free Plan
        free_plan = db.query(Plan).filter(Plan.name == "Free").first()
        if not free_plan:
            free_plan = Plan(name="Free", credits=10)
            db.add(free_plan)
            db.commit()
            db.refresh(free_plan)

        # Create Admin
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            admin_email = os.getenv("ADMIN_EMAIL")
            admin_password = os.getenv("ADMIN_PASSWORD")

            if admin_email and admin_password:
                hashed_password = get_password_hash(admin_password)

                new_admin = User(
                    email=admin_email,
                    hashed_password=hashed_password,
                    role="admin",
                    credits=9999,
                    plan_id=free_plan.id
                )
                db.add(new_admin)
                db.commit()

    except Exception as e:
        print("Init error:", e)

    finally:
        db.close()

# --------------------------------------------------
# Startup Event (NON-BLOCKING)
# --------------------------------------------------

@app.on_event("startup")
def startup_event():
    # Run DB initialization in background thread
    threading.Thread(target=init_data_background).start()

# --------------------------------------------------
# Health Check (Important for Render)
# --------------------------------------------------

@app.get("/health")
def health():
    return {"status": "ok"}

# --------------------------------------------------
# Routes
# --------------------------------------------------

@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request}
    )

@app.get("/admin", response_class=HTMLResponse)
def admin_panel(request: Request):
    return templates.TemplateResponse(
        "admin.html",
        {"request": request}
    )
