from fastapi import APIRouter
from database import sales_collection, expense_collection

router = APIRouter()

@router.get("/branch-ranking")
def ranking():
    sales = list(sales_collection.find())
    expenses = list(expense_collection.find())

    branch_profit = {}

    for s in sales:
        bid = s.get("branchId")
        if bid:
            branch_profit[bid] = branch_profit.get(bid, 0) + s.get("totalAmount", 0)

    for e in expenses:
        bid = e.get("branchId")
        if bid:
            branch_profit[bid] = branch_profit.get(bid, 0) - e.get("amount", 0)

    ranked = sorted(branch_profit.items(), key=lambda x: x[1], reverse=True)
    
    # Return as list of objects for easier frontend mapping
    return [{"branchId": k, "profit": v} for k, v in ranked]
