import sys
import os
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

# CRITICAL: This line tells Python exactly where your code is
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Now we can import our routers safely
from routers import auth, converter, admin, dashboard

app = FastAPI(title="Accountesy")

# Mount static files for your logo.png and b-logo.png
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(converter.router)
app.include_router(admin.router)

@app.get("/")
async def public_landing(request: Request):
    # This serves your landing page with the Debasish Biswas footer
    return templates.TemplateResponse("landing.html", {"request": request})
