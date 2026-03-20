from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.parser import parse_statement
from master_parser import parse_master
from mapping_engine import map_transactions
from xml_generator import generate_tally_xml

import os
import shutil

app = FastAPI()

# CORS (optional safe)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/process")
async def process(file: UploadFile = File(...), master: UploadFile = File(None)):
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

# 👉 SERVE FRONTEND (IMPORTANT)
app.mount("/", StaticFiles(directory="../dist", html=True), name="static")
