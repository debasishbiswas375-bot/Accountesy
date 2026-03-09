from fastapi import APIRouter, Form

router = APIRouter(prefix="/admin")

@router.get("/")
def admin_dashboard():

    return {
        "users":120,
        "conversions":560
    }

@router.post("/user/update")

def update_user(
    user_id:int = Form(...),
    email:str = Form(...),
    credits:int = Form(...)
):

    return {"status":"user updated"}
