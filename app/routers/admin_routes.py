from fastapi import APIRouter
router=APIRouter()

@router.get("/admin")
def admin():
    return {"admin":"panel"}
