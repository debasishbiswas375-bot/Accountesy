from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import auth, converter, admin, dashboard

app = FastAPI(title="Accountesy", description="Bank Statement to Tally XML Converter")

# Mount Static Files (CSS, JS, Images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include all modular routers
app.include_router(dashboard.router)
app.include_router(auth.router)
app.include_router(converter.router)
app.include_router(admin.router)
