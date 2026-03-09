from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from app.routers import auth, converter, admin, dashboard

app = FastAPI(title="Accountesy")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(converter.router)
app.include_router(admin.router)

@app.get("/")
async def public_landing(request: Request):
    # This serves your public marketing page to everyone!
    return templates.TemplateResponse("landing.html", {"request": request})
