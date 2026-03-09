from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.routers import landing_routes
from app.routers import auth_routes
from app.routers import dashboard_routes
from app.routers import workspace_routes
from app.routers import history_routes
from app.routers import admin_routes
from app.routers import plans_routes

app = FastAPI(title="Accountesy – Accounting Expert")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(landing_routes.router)
app.include_router(auth_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(workspace_routes.router)
app.include_router(history_routes.router)
app.include_router(admin_routes.router)
app.include_router(plans_routes.router)
