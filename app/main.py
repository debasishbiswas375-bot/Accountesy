from fastapi.responses import FileResponse
import os
import pandas as pd
from fastapi import FastAPI, Request, UploadFile, File, Form
from fastapi.responses import HTMLResponse, StreamingResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import io, json

from app.database import supabase
from app.tools.mapper import smart_map_bank
from app.tools.engine import assign_ledger, learn_pattern
from app.tools.preview import calculate_cost, get_preview

app = FastAPI()

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")

# Temporary storage per user
TEMP_STORAGE = {}

# =========================
# 🏠 LANDING PAGE
# =========================
@app.get("/")
def landing(request: Request):
    return templates.TemplateResponse("landing.html", {"request": request})


# =========================
# 🔐 AUTH PAGE (UI)
# =========================
@app.get("/auth")
def auth_page(request: Request):
    return templates.TemplateResponse("auth.html", {"request": request})


# =========================
# 🔑 LOGIN (SET COOKIE)
# =========================
@app.post("/login")
async def login(email: str = Form(...), password: str = Form(...)):
    try:
        supabase.auth.sign_in_with_password({
            "email": email,
            "password": password
        })

        response = RedirectResponse(url="/workspace", status_code=302)
        response.set_cookie(key="user", value=email)

        return response

    except:
        return {"error": "Invalid credentials"}


# =========================
# 📝 REGISTER
# =========================
@app.post("/register")
async def register(
    username: str = Form(...),
    email: str = Form(...),
    password: str = Form(...)
):
    try:
        res = supabase.auth.sign_up({
            "email": email,
            "password": password
        })

        user_id = res.user.id

        supabase.table("users").insert({
            "id": user_id,
            "username": username,
            "credits": 10,
            "plan": "Free"
        }).execute()

        return {"status": "success"}

    except Exception as e:
        print(e)
        return {"error": "Registration failed"}


# =========================
# 🚪 LOGOUT
# =========================
@app.get("/logout")
def logout():
    response = RedirectResponse(url="/")
    response.delete_cookie("user")
    return response


# =========================
# 🧩 WORKSPACE
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
    df = smart_map_bank(content, file.filename)

    user_id = request.cookies.get("user") or "guest_user"

    df["ledger_name"] = df.apply(
        lambda row: assign_ledger(row, user_id), axis=1
    )

    total, cost = calculate_cost(df)

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
# 📥 FINAL CONVERT
# =========================
@app.post("/workspace/final-convert")
async def final_convert(
    request: Request,
    filename: str = Form(...),
    changes: str = Form(...)
):

    user_id = request.cookies.get("user")

    # 🔐 BLOCK GUEST
    if not user_id:
        return RedirectResponse(url="/auth", status_code=302)

    df = TEMP_STORAGE.get(user_id)

    if df is None:
        return {"error": "Session expired"}

    changes = json.loads(changes)

    for idx, new_ledger in changes.items():
        idx = int(idx)
        old_desc = df.iloc[idx]["description"]

        df.at[idx, "ledger_name"] = new_ledger

        # AI learning
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

    # Deduct
    supabase.table("users").update({
        "credits": user["credits"] - cost
    }).eq("id", user_id).execute()

    # =========================
    # 📄 XML GENERATE
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

    # Keep last 3 downloadable
    history = supabase.table("conversion_history") \
        .select("*") \
        .eq("user_id", user_id) \
        .order("created_at", desc=True) \
        .execute()

    if len(history.data) > 3:
        for item in history.data[3:]:
            supabase.table("conversion_history").update({
                "xml_data": None
            }).eq("id", item["id"]).execute()

    return StreamingResponse(
        io.BytesIO(xml_data.encode()),
        media_type="application/xml",
        headers={
            "Content-Disposition": f"attachment; filename={filename}.xml"
        }
    )


# =========================
# 📝 FEEDBACK
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
# =========================
# 📊 EXCEL TOOL ROUTE
# =========================
@app.get("/excel", response_class=HTMLResponse)
async def excel_page(request: Request):
    return templates.TemplateResponse("excel.html", {"request": request})


# =========================
# 📂 PDF → EXCEL
# =========================
@app.post("/convert-excel")
async def convert_excel(file: UploadFile = File(...)):
    content = await file.read()

    df = smart_map_bank(content, file.filename)

    output_path = f"{file.filename}.xlsx"
    df.to_excel(output_path, index=False)

    return FileResponse(
        output_path,
        filename="converted.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


# =========================
# 📂 PDF → XML
# =========================
@app.post("/convert-xml")
async def convert_xml(file: UploadFile = File(...)):
    content = await file.read()

    df = smart_map_bank(content, file.filename)

    xml = "<VOUCHERS>\n"

    for _, row in df.iterrows():
        xml += f"""
<VOUCHER>
    <DATE>{row.get('date','')}</DATE>
    <NARRATION>{row.get('description','')}</NARRATION>
    <AMOUNT>{row.get('amount','')}</AMOUNT>
</VOUCHER>
"""

    xml += "\n</VOUCHERS>"

    return StreamingResponse(
        io.BytesIO(xml.encode()),
        media_type="application/xml",
        headers={"Content-Disposition": "attachment; filename=converted.xml"}
    )
