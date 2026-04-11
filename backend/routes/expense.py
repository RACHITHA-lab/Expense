from fastapi import APIRouter
from database import expense_collection

router = APIRouter()

@router.post("/add-expense")
def add_expense(data: dict):
    expense_collection.insert_one(data)
    return {"message": "Expense added"}

@router.get("/expenses")
def get_expense():
    return list(expense_collection.find({}, {"_id": 0}))
