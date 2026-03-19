from fastapi import APIRouter

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.get("/login")
def login():
    return {"message": "User login system coming soon"}
