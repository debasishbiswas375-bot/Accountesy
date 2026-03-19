from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
import io
from app.database import supabase
from app.tools.mapper import smart_map_bank
from app.tools.engine import assign_ledger, learn_pattern
from app.tools.preview import calculate_cost, get_preview

app = FastAPI()
templates = Jinja2Templates(directory="app/templates")

TEMP_STORAGE = {}  # temporary session storage


# 🧩 WORKSPACE
@app.get("/workspace", response_class=HTMLResponse)
async def workspace(request: Request):
    return templates.TemplateResponse("workspace.html", {"request": request})


# 🧩 CONVERT → PREVIEW
@app.post("/workspace/convert")
async def convert_file(request: Request, file: UploadFile = File(...)):

    content = await file.read()

    df = smart_map_bank(content, file.filename)

    user_id = "demo_user"  # replace with auth later

    df["ledger_name"] = df.apply(
        lambda row: assign_ledger(row, user_id), axis=1
    )

    total, cost = calculate_cost(df)

    # store temp
    TEMP_STORAGE[user_id] = df

    preview = get_preview(df)

    return templates.TemplateResponse("workspace_preview.html", {
        "request": request,
        "preview": preview,
        "total_rows": total,
        "cost": cost,
        "filename": file.filename
    })


# 🧠 FINAL CONVERT + DOWNLOAD
@app.post("/workspace/final-convert")
async def final_convert(request: Request, filename: str = Form(...)):

    user_id = "demo_user"

    df = TEMP_STORAGE.get(user_id)

    total, cost = calculate_cost(df)

    # 🔥 CREDIT CHECK
    user = supabase.table("users").select("*").eq("id", user_id).single().execute().data

    if user["credits"] < cost:
        return {"error": "Not enough credits"}

    # 🔥 DEDUCT CREDITS
    supabase.table("users").update({
        "credits": user["credits"] - cost
    }).eq("id", user_id).execute()

    # 🔥 GENERATE XML
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

    # 🔥 SAVE HISTORY
    res = supabase.table("conversion_history").insert({
        "user_id": user_id,
        "filename": filename,
        "total_rows": total,
        "credits_used": cost,
        "xml_data": xml_data
    }).execute()

    # 🔥 KEEP ONLY LAST 3 DOWNLOADABLE
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

    # 🔥 RETURN FILE
    return StreamingResponse(
        io.BytesIO(xml_data.encode()),
        media_type="application/xml",
        headers={"Content-Disposition": f"attachment; filename={filename}.xml"}
    )
