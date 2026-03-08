from fastapi import APIRouter
router=APIRouter()

@router.get("/login")
def login():
    return {"login":"page"}

@router.get("/register")
def register():
    return {"register":"page"}
