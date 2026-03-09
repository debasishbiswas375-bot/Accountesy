from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.routers import pages_routes,auth_routes,dashboard_routes,convert_routes,plans_routes,admin_routes

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(pages_routes.router)
app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(convert_routes.router)
app.include_router(plans_routes.router)
app.include_router(admin_routes.router)
