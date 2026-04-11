from fastapi import APIRouter
from database import sales_collection, expense_collection

router = APIRouter()

@router.get("/analytics")
def analytics():
    sales = list(sales_collection.find())
    expenses = list(expense_collection.find())

    total_sales = sum(s.get("totalAmount", 0) for s in sales)
    total_expense = sum(e.get("amount", 0) for e in expenses)
    profit = total_sales - total_expense

    # Top products
    product_sales = {}
    for s in sales:
        pid = s.get("productId")
        if pid:
            product_sales[pid] = product_sales.get(pid, 0) + s.get("quantity", 0)

    top_products = sorted(product_sales.items(), key=lambda x: x[1], reverse=True)[:5]

    return {
        "totalSales": total_sales,
        "totalExpense": total_expense,
        "profit": profit,
        "topProducts": top_products
    }
