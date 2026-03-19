from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import os
import json

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")

HISTORY_FILE = "app/data/history.json"
os.makedirs("app/data", exist_ok=True)

# Ensure file exists
if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w") as f:
        json.dump([], f)


# =========================
# PAGE
# =========================
@router.get("/history", response_class=HTMLResponse)
def history_page(request: Request):
    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)

    return templates.TemplateResponse("history.html", {
        "request": request,
        "history": data
    })


# =========================
# API: GET HISTORY
# =========================
@router.get("/history-data")
def get_history():
    with open(HISTORY_FILE, "r") as f:
        return json.load(f)


# =========================
# API: SAVE HISTORY
# =========================
@router.post("/save-history")
def save_history(item: dict):
    with open(HISTORY_FILE, "r") as f:
        data = json.load(f)

    data.append(item)

    with open(HISTORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

    return {"status": "saved"}
