from fastapi import FastAPI, UploadFile, File, HTTPException, Header
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from backend.parser import parse_statement
from backend.master_parser import parse_master
from backend.mapping_engine import map_transactions
from backend.xml_generator import generate_tally_xml

from backend.auth import hash_password, verify_password, create_access_token, decode_access_token
from backend.db import supabase

import os
import shutil

app = FastAPI()

# ==========================
# CORS
# ==========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# ==========================
# 🚀 SIGNUP
# ==========================
@app.post("/signup")
def signup(data: dict):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(400, "Email and password required")

    existing = supabase.table("users").select("id").eq("email", email).execute()

    if existing.data:
        raise HTTPException(400, "User already exists")

    supabase.table("users").insert({
        "email": email,
        "hashed_password": hash_password(password),
        "username": data.get("username"),
        "phone": data.get("contact"),
        "address": data.get("address"),
        "pincode": data.get("pincode"),
        "district": data.get("district"),
        "state": data.get("state"),
        "country": data.get("country"),
        "role": "user",
        "credits": 100,
        "is_active": True,
        "is_deleted": False
    }).execute()

    return {"status": "user created"}


# ==========================
# 🚀 LOGIN
# ==========================
@app.post("/login")
def login(data: dict):
    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        raise HTTPException(400, "Missing credentials")

    res = supabase.table("users").select("*").eq("email", email).execute()

    if not res.data:
        raise HTTPException(401, "Invalid email")

    user = res.data[0]

    if not user.get("is_active") or user.get("is_deleted"):
        raise HTTPException(403, "Account disabled")

    if not verify_password(password, user["hashed_password"]):
        raise HTTPException(401, "Wrong password")

    token = create_access_token(str(user["id"]), user.get("role", "user"))

    return {
        "status": "success",
        "token": token,
        "user": {
            "email": user["email"],
            "credits": user.get("credits", 0),
            "role": user.get("role", "user")
        }
    }


# ==========================
# 🚀 TOKEN VALIDATION
# ==========================
def get_current_user(token: str = Header(...)):
    payload = decode_access_token(token)
    if not payload:
        raise HTTPException(401, "Invalid token")
    return payload


# ==========================
# 🚀 MAIN PROCESS (PROTECTED)
# ==========================
@app.post("/process")
async def process(
    file: UploadFile = File(...),
    master: UploadFile = File(None),
    token: str = Header(...)
):
    user = get_current_user(token)

    file_path = os.path.join(UPLOAD_DIR, file.filename)

    with open(file_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    transactions = parse_statement(file_path)

    masters = []
    if master:
        master_path = os.path.join(UPLOAD_DIR, master.filename)
        with open(master_path, "wb") as f:
            shutil.copyfileobj(master.file, f)
        masters = parse_master(master_path)

    mapped = map_transactions(transactions, masters)
    xml = generate_tally_xml(mapped)

    return {
        "data": mapped,
        "xml": xml
    }


# ==========================
# 🚀 SERVE FRONTEND (DYNAMIC PATHING FIX)
# ==========================

# 1. Dynamically find the absolute path to the root folder (one level up from backend/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DIST_DIR = os.path.join(BASE_DIR, "dist")
ASSETS_DIR = os.path.join(DIST_DIR, "assets")

# 2. Mount the assets folder safely if it exists
if os.path.exists(ASSETS_DIR):
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# 3. Smart Catch-all route for React (SPA)
@app.get("/{full_path:path}")
def serve_react_routes(full_path: str):
    # Check if the exact file exists (e.g., vite.svg, robots.txt)
    specific_file = os.path.join(DIST_DIR, full_path)
    if os.path.isfile(specific_file):
        return FileResponse(specific_file)
    
    # Otherwise, fall back to index.html to let React Router handle the URL
    index_file = os.path.join(DIST_DIR, "index.html")
    if os.path.isfile(index_file):
        return FileResponse(index_file)
        
    # If we get here, the dist folder doesn't exist on the server
    return JSONResponse(
        status_code=404, 
        content={"error": "Frontend build not found. The 'dist' folder is missing. Ensure 'npm run build' runs during deployment."}
    )
