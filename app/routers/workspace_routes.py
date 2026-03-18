@router.post("/final-convert")
async def finalize_conversion(request: Request, filename: str = Form(...)):

    user = request.cookies.get("user")

    if not user:
        return RedirectResponse(url="/auth", status_code=302)

    # ✅ Logged in → allow
    from app.tools.converter import build_tally_xml

    return {"message": f"{filename} ready for download"}
