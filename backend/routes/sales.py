from fastapi import APIRouter, Query
from database import sales_collection
from typing import Optional

router = APIRouter()

@router.post("/add-sale")
def add_sale(data: dict):
    sales_collection.insert_one(data)
    return {"message": "Sale added"}

@router.get("/sales")
def get_sales(branchId: Optional[str] = Query(None)):
    # Professional filtering!
    query = {}
    if branchId:
        query["branchId"] = branchId
        
    sales = list(sales_collection.find(query, {"_id": 0}))
    if not sales:
        return {"message": "No data found", "data": []}
    return {"data": sales}
