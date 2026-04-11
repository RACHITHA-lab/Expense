from fastapi import APIRouter
from database import inventory_collection
from utils.predict import predict_demand
import os
import pickle

router = APIRouter()

# Local model load for alerts ML integration 
model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "demand_model.pkl")
try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
except Exception:
    model = None

@router.get("/alerts")
def alerts():
    alerts_data = []

    inventory = list(inventory_collection.find())

    for item in inventory:
        stock = item.get("stockQuantity", 0)
        
        # Using .get for missing fields to avoid KeyErrors
        if stock < item.get("minStockLevel", 10):
            alerts_data.append({
                "type": "LOW_STOCK",
                "productId": item.get("productId", "Unknown"),
                "message": "Stock below minimum"
            })

        if stock > item.get("maxStockLevel", 9999):
            alerts_data.append({
                "type": "OVERSTOCK",
                "productId": item.get("productId", "Unknown")
            })

    # ML Alert
    if model:
        for item in inventory:
            stock = item.get("stockQuantity", 0)
            predicted = predict_demand(model, 100, 400, stock)
            if predicted > stock:
                alerts_data.append({
                    "type": "DEMAND_HIGH",
                    "productId": item.get("productId", "Unknown"),
                    "message": f"Predicted demand {predicted:.1f} exceeds stock {stock}"
                })

    return {"alerts": alerts_data}
