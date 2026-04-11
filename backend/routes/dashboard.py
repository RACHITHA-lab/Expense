from fastapi import APIRouter
from database import sales_collection, expense_collection

router = APIRouter()

@router.get("/dashboard-summary")
def dashboard():
    sales = list(sales_collection.find())
    expenses = list(expense_collection.find())

    total_sales = sum(s.get("totalAmount", 0) for s in sales)
    total_expense = sum(e.get("amount", 0) for e in expenses)

    return {
        "totalSales": total_sales,
        "totalExpense": total_expense,
        "profit": total_sales - total_expense,
        "totalTransactions": len(sales)
    }
