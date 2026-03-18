.guest-blur {
    filter: blur(3px);
    pointer-events: none;
}
from supabase import create_client
import os
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import io, json

from app.database import supabase
from app.tools.mapper import smart_map_bank
from app.tools.engine import assign_ledger, learn_pattern
from app.tools.preview import calculate_cost, get_preview

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

# Temporary storage (per user session)
TEMP_STORAGE = {}


# =========================
# 🧩 WORKSPACE PAGE
# =========================
@app.get("/workspace", response_class=HTMLResponse)
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})


# =========================
# 🔄 UPLOAD → PREVIEW
# =========================
@app.post("/workspace/convert")
async def convert_file(request: Request, file: UploadFile = File(...)):

    content = await file.read()

    # Normalize file
    df = smart_map_bank(content, file.filename)

    user_id = "demo_user"  # TODO: replace with auth system

    # Assign ledgers
    df["ledger_name"] = df.apply(
        lambda row: assign_ledger(row, user_id), axis=1
    )

    total, cost = calculate_cost(df)

    # Store temporarily
    TEMP_STORAGE[user_id] = df

    preview = get_preview(df)

    return templates.TemplateResponse("workspace_preview.html", {
        "request": request,
        "preview": preview,
        "total_rows": total,
        "cost": cost,
        "filename": file.filename
    })


# =========================
# 📥 FINAL CONVERT + DOWNLOAD
# =========================
@app.post("/workspace/final-convert")
async def final_convert(
    request: Request,
    filename: str = Form(...),
    changes: str = Form(...)
):
    user_id = "demo_user"

    df = TEMP_STORAGE.get(user_id)

    if df is None:
        return {"error": "Session expired. Please upload again."}

    # Apply user changes
    changes = json.loads(changes)

    for idx, new_ledger in changes.items():
        idx = int(idx)
        old_desc = df.iloc[idx]["description"]

        df.at[idx, "ledger_name"] = new_ledger

        # 🔥 LEARNING (always for now except forced default logic)
        learn_pattern(user_id, old_desc, new_ledger)

    total, cost = calculate_cost(df)

    # =========================
    # 💰 CREDIT CHECK
    # =========================
    user_res = supabase.table("users") \
        .select("*") \
        .eq("id", user_id) \
        .single() \
        .execute()

    user = user_res.data

    if user["credits"] < cost:
        return {"error": "Not enough credits"}

    # Deduct credits
    supabase.table("users").update({
        "credits": user["credits"] - cost
    }).eq("id", user_id).execute()

    # =========================
    # 📄 XML GENERATION
    # =========================
    xml_data = "<VOUCHERS>\n"

    for _, row in df.iterrows():
        xml_data += f"""
<VOUCHER>
    <DATE>{row['date']}</DATE>
    <LEDGER>{row['ledger_name']}</LEDGER>
    <AMOUNT>{row['amount']}</AMOUNT>
</VOUCHER>
"""

    xml_data += "\n</VOUCHERS>"

    # =========================
    # 🗄️ SAVE HISTORY
    # =========================
    supabase.table("conversion_history").insert({
        "user_id": user_id,
        "filename": filename,
        "total_rows": total,
        "credits_used": cost,
        "xml_data": xml_data
    }).execute()

    # =========================
    # 🔥 KEEP ONLY LAST 3 DOWNLOADABLE
    # =========================
    history = supabase.table("conversion_history") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .execute()

    if len(history.data) > 3:
        old_ids = [item["id"] for item in history.data[3:]]
        for oid in old_ids:
            supabase.table("conversion_history").update({
                "xml_data": None
            }).eq("id", oid).execute()

    # =========================
    # 📤 RETURN FILE
    # =========================
    return StreamingResponse(
        io.BytesIO(xml_data.encode()),
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.xml"
        }
    )


# =========================
# 📝 FEEDBACK SYSTEM
# =========================
@app.post("/submit-feedback")
async def submit_feedback(
    name: str = Form(...),
    email: str = Form(...),
    contact: str = Form(...),
    message: str = Form(...)
):
    try:
        supabase.table("feedback").insert({
            "name": name,
            "email": email,
            "contact": contact,
            "message": message
        }).execute()

        return {"status": "success"}

    except Exception as e:
        print("Feedback Error:", e)
        return {"status": "error"}
