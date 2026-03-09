from fastapi import APIRouter
from app.database import get_db

router = APIRouter()

@router.get("/plans")

def get_plans():

    db = get_db()

    result = db.execute("""
        SELECT id,name,credits,price,duration_days
        FROM plans
        WHERE active = TRUE
        ORDER BY price
    """).fetchall()

    plans = []

    for p in result:

        plans.append({
            "id":p[0],
            "name":p[1],
            "credits":p[2],
            "price":p[3],
            "duration":p[4]
        })

    return plans
