from fastapi import APIRouter
from database import product_collection

router = APIRouter()

supplier_collection = product_collection.database["suppliers"]

@router.post("/add-supplier")
def add_supplier(data: dict):
    supplier_collection.insert_one(data)
    return {"message": "Supplier added successfully"}

@router.get("/suppliers")
def get_suppliers():
    """
    Returns supplier data and analyzes risk if delivery defaults are high.
    Bonus feature.
    """
    suppliers = list(supplier_collection.find({}, {"_id": 0}))
    for s in suppliers:
        defaults = s.get("missedDeliveries", 0)
        s["riskStatus"] = "High Risk" if defaults > 3 else "Safe"
        
    return suppliers
