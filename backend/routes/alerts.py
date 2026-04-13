from fastapi import APIRouter
from database import inventory_collection, sales_collection
from utils.predict import predict_demand
import os
import pickle
from datetime import datetime

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
    
    seasonality = 1
    day_of_week = datetime.now().weekday()
    festival_effect = 0

    for item in inventory:
        stock = item.get("stockQuantity", 0)
        product_id = item.get("productId", "Unknown")
        branch_id = item.get("branchId", "Unknown")
        
        predicted = 0
        if model:
            predicted = predict_demand(
                model, 
                item.get("lastWeekSales", 50), 
                item.get("lastMonthSales", 200), 
                stock, 
                seasonality, 
                day_of_week, 
                festival_effect
            )
            
        # 1. Low Stock (Dynamic Reorder Level)
        lead_time = item.get("leadTimeDays", 3)
        safety_stock = item.get("safetyStock", 20)
        dynamic_reorder = (predicted / 7) * lead_time + safety_stock
        
        if stock < dynamic_reorder:
            alerts_data.append({
                "type": "LOW_STOCK",
                "severity": "Critical" if stock < (dynamic_reorder / 2) else "High",
                "productId": product_id,
                "branchId": branch_id,
                "message": f"Stock ({stock}) below dynamic reorder level ({int(dynamic_reorder)})"
            })

        # 2. Overstock
        if predicted > 0 and stock > (predicted * 2):
            alerts_data.append({
                "type": "OVERSTOCK",
                "severity": "Medium",
                "productId": product_id,
                "branchId": branch_id,
                "message": f"Excess stock ({stock}) for predicted demand ({int(predicted)})"
            })
            
        # 3. Dead Stock (Industry Standard Logic)
        if stock > 0:
            all_sales = list(sales_collection.find({"productId": product_id}).sort("saleDate", -1))
            
            if not all_sales:
                # No sales ever -> New Product, NOT Dead Stock
                pass 
            else:
                last_sale_str = all_sales[0].get("saleDate")
                if last_sale_str:
                    try:
                        if isinstance(last_sale_str, str):
                            last_sale_date = datetime.fromisoformat(last_sale_str.replace("Z", "+00:00")).replace(tzinfo=None)
                        else:
                            last_sale_date = last_sale_str.replace(tzinfo=None)
                        
                        days_since_sale = (datetime.now() - last_sale_date).days
                        
                        # Dynamic limit: could be 30, or scaled. Let's use 30 as fixed threshold.
                        if days_since_sale > 30:
                            alerts_data.append({
                                "type": "DEAD_STOCK",
                                "severity": "High",
                                "productId": product_id,
                                "branchId": branch_id,
                                "message": f"No sales for {days_since_sale} days. Stock is stagnant."
                            })
                    except Exception:
                        pass
            
        # 4. High Demand
        if stock > 0 and predicted > (stock * 1.5):
            alerts_data.append({
                "type": "DEMAND_HIGH",
                "severity": "Critical",
                "productId": product_id,
                "branchId": branch_id,
                "message": f"Predicted demand {int(predicted)} far exceeds stock {stock}"
            })

    return {"alerts": alerts_data}

from routes.inventory import detect_dead_stock

@router.get("/alerts/{product_id}")
def get_alerts(product_id: str):
    # Fetch inventory data for this product
    inventory_data = list(inventory_collection.find({"productId": product_id}, {"_id": 0}))

    # Calculate total stock
    total_stock = sum(item.get("stockQuantity", 0) for item in inventory_data)

    # Detect dead stock (fixed call ✅)
    dead_stock_status = detect_dead_stock(product_id)

    alerts = []

    # Low stock alert
    for item in inventory_data:
        # Assuming minStockLevel is the target, applying as 'reorder_level'
        reorder_level = item.get("minStockLevel", 40)
        stock = item.get("stockQuantity", 0)
        
        if stock < reorder_level:
            alerts.append({
                "type": "LOW_STOCK",
                "branch": item.get("branchId", "Unknown"),
                "stock": stock
            })

    # Dead stock alert
    if dead_stock_status == True:
        alerts.append({"type": "DEAD_STOCK"})
    elif dead_stock_status == "NEW_PRODUCT":
        alerts.append({"type": "NEW_PRODUCT"})

    return {
        "product_id": product_id,
        "total_stock": total_stock,
        "alerts": alerts
    }

