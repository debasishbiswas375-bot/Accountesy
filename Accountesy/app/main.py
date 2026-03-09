from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
# Relative imports work best when Root Directory is set to Accountesy/
from app.routers import auth, converter, admin, dashboard

app = FastAPI(title="Accountesy")

# Since Render is "inside" the Accountesy folder, we mount /static directly
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates location for the Jinja2 engine
templates = Jinja2Templates(directory="templates")

# Include all your functional routers
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(converter.router)
app.include_router(admin.router)

@app.get("/")
async def public_landing(request: Request):
    """
    Serves the premium glassmorphism landing page to all visitors.
    Includes the footer created by Debasish Biswas and sponsorship branding.
    """
    return templates.TemplateResponse("landing.html", {"request": request})
