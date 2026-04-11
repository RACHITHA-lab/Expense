from fastapi import APIRouter, Query, HTTPException
from database import inventory_collection, sales_collection
from utils.predict import predict_demand
from typing import Optional
import os
import pickle
from datetime import datetime, timedelta

router = APIRouter()

model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "demand_model.pkl")
try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
except Exception:
    model = None

@router.post("/update-stock")
def update_stock(data: dict):
    product_id = data.get("productId")
    branch_id = data.get("branchId")

    if not product_id or not branch_id:
        inventory_collection.insert_one(data)
        return {"message": "Stock added"}

    inventory_collection.update_one(
        {"productId": product_id, "branchId": branch_id},
        {"$set": data},
        upsert=True,
    )
    return {"message": "Stock updated"}


@router.post("/restock")
def restock(data: dict):
    return adjust_stock(data, 1)


@router.post("/reduce-stock")
def reduce_stock(data: dict):
    return adjust_stock(data, -1)


def adjust_stock(data: dict, direction: int):
    if "productId" not in data or "branchId" not in data:
        raise HTTPException(status_code=400, detail="productId and branchId are required")

    quantity = abs(int(data.get("quantity", 1)))
    if direction < 0:
        quantity = -quantity

    result = inventory_collection.update_one(
        {"productId": data["productId"], "branchId": data["branchId"]},
        {"$inc": {"stockQuantity": quantity}},
    )

    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Inventory item not found")

    return {"message": "Stock updated", "stockChange": quantity}


@router.post("/transfer")
def transfer(data: dict):
    product_id = data.get("productId")
    from_branch = data.get("fromBranchId")
    to_branch = data.get("toBranchId")
    quantity = abs(int(data.get("quantity", 1)))

    if not product_id or not from_branch or not to_branch:
        raise HTTPException(status_code=400, detail="productId, fromBranchId, and toBranchId are required")
    if from_branch == to_branch:
        raise HTTPException(status_code=400, detail="Source and destination branch must differ")

    remove_result = inventory_collection.update_one(
        {"productId": product_id, "branchId": from_branch},
        {"$inc": {"stockQuantity": -quantity}},
    )
    if remove_result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Source inventory item not found")

    inventory_collection.update_one(
        {"productId": product_id, "branchId": to_branch},
        {"$inc": {"stockQuantity": quantity}},
        upsert=True,
    )

    return {"message": "Stock transferred", "transferred": quantity}


@router.delete("/delete-inventory/{product_id}/{branch_id}")
def delete_inventory(product_id: str, branch_id: str):
    result = inventory_collection.delete_one({"productId": product_id, "branchId": branch_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Inventory item not found")
    return {"message": "Inventory item removed"}


@router.get("/inventory")
def get_inventory():
    items = list(inventory_collection.find({}, {"_id": 0}))
    return items


def calculate_stock_health(stock, min_stock):
    if stock <= min_stock:
        return "Red"
    elif stock <= min_stock * 1.5:
        return "Yellow"
    else:
        return "Green"


def classify_stock(stock):
    if stock < 10:
        return "Critical"
    elif stock < 30:
        return "Low"
    elif stock > 200:
        return "Overstock"
    else:
        return "Normal"


def forecast_days(stock, avg_daily_sales):
    if avg_daily_sales == 0:
        return "No Data"
    return round(stock / avg_daily_sales, 1)


def generate_recommendation(stock, predicted):
    if predicted > stock:
        return "Restock Immediately"
    elif stock > predicted * 2:
        return "Reduce Stock"
    else:
        return "Stock Balanced"


def detect_dead_stock(product_id):
    """Detect if product is not selling at all by checking sales collection."""
    last_30_days = datetime.now() - timedelta(days=30)
    
    try:
        sales = list(sales_collection.find({
            "productId": product_id,
            "saleDate": {"$gte": last_30_days}
        }))
        return len(sales) == 0
    except:
        # Fallback: check last_30_days_sales field if saleDate not available
        return False


def classify_demand(predicted):
    """Classify demand level based on prediction."""
    if predicted >= 200:
        return "High Demand"
    elif predicted >= 100:
        return "Medium Demand"
    elif predicted >= 50:
        return "Low Demand"
    else:
        return "Very Low Demand"


def calculate_inventory_value(stock, cost_price):
    """Calculate total inventory value."""
    if cost_price is None or cost_price == 0:
        return 0
    return round(stock * cost_price, 2)


def calculate_health_score(stock, predicted):
    """Calculate inventory health score (0-100)."""
    if predicted == 0:
        return 50
    ratio = (stock / predicted) * 100
    return min(100, max(0, round(ratio, 1)))


def check_expiry_status(expiry_date_str):
    """Check if product is expiring soon (within 5 days)."""
    if not expiry_date_str:
        return "No Expiry Info"
    try:
        expiry_date = datetime.fromisoformat(expiry_date_str)
        today = datetime.now()
        days_left = (expiry_date - today).days
        if days_left < 0:
            return "Expired"
        elif days_left <= 5:
            return "Expiring Soon"
        else:
            return "Fresh"
    except:
        return "No Expiry Info"


def get_transfer_suggestions(product_id, current_branch, current_stock, items):
    """Find branches with excess stock of same product."""
    suggestions = []
    for item in items:
        if (item.get("productId") == product_id and 
            item.get("branchId") != current_branch):
            other_stock = item.get("stockQuantity", 0)
            if other_stock > 100 and current_stock < 30:
                suggestions.append({
                    "fromBranch": item.get("branchId"),
                    "quantity": min(50, other_stock - 50),
                    "reason": f"Transfer {min(50, other_stock - 50)} from {item.get('branchId')}"
                })
    return suggestions[0] if suggestions else None


def smart_inventory_logic(item: dict, all_items: list = None):
    stock = item.get("stockQuantity", 0)
    min_stock = item.get("minStockLevel", 0)
    last_week = item.get("lastWeekSales", 120)
    last_month = item.get("lastMonthSales", 500)
    avg_daily_sales = item.get("avgDailySales", 10)
    cost_price = item.get("costPrice", 0)
    expiry_date = item.get("expiryDate")
    product_id = item.get("productId")

    predicted = 0
    if model:
        predicted = predict_demand(model, last_week, last_month, stock)

    # Core smart fields
    item["predictedDemand"] = round(predicted, 2)
    item["stockHealth"] = calculate_stock_health(stock, min_stock)
    item["stockStatus"] = classify_stock(stock)
    item["forecastDays"] = forecast_days(stock, avg_daily_sales)
    item["recommendation"] = generate_recommendation(stock, predicted)

    # 🔥 NEW FEATURES 🔥

    # 1. Dead Stock Detection (query actual sales data)
    item["isDeadStock"] = detect_dead_stock(product_id)
    
    # 2. Demand Classification
    item["demandCategory"] = classify_demand(predicted)
    
    # 3. Inventory Value
    item["inventoryValue"] = calculate_inventory_value(stock, cost_price)
    
    # 4. Health Score
    item["healthScore"] = calculate_health_score(stock, predicted)
    
    # 5. Expiry Status
    item["expiryStatus"] = check_expiry_status(expiry_date)
    
    # 6. Stock-Out Prediction
    if avg_daily_sales > 0:
        item["stockOutDays"] = round(stock / avg_daily_sales, 1)
    else:
        item["stockOutDays"] = "N/A"
    
    # 7. Transfer Suggestion
    if all_items:
        transfer = get_transfer_suggestions(
            item.get("productId"), 
            item.get("branchId"), 
            stock, 
            all_items
        )
        item["transferSuggestion"] = transfer
    
    # 8. Enhanced Recommendation Engine
    if item.get("isDeadStock"):
        item["recommendation"] = "Apply Discount / Clearance Sale"
        item["actionPriority"] = "High"
    elif item.get("expiryStatus") == "Expiring Soon":
        item["recommendation"] = "Apply 20% Discount - Expiring Soon"
        item["actionPriority"] = "Critical"
    elif predicted > stock:
        item["recommendation"] = f"Restock {int(predicted - stock)} units"
        item["actionPriority"] = "High"
    elif stock > predicted * 2:
        item["recommendation"] = f"Reduce stock by {int(stock - predicted)} units"
        item["actionPriority"] = "Medium"
    else:
        item["recommendation"] = "Stock Balanced"
        item["actionPriority"] = "Low"

    return item


@router.get("/smart-inventory")
def smart_inventory(
    branchId: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
):
    query = {}
    if branchId:
        query["branchId"] = branchId
    if category:
        query["category"] = category
    if search:
        query["productId"] = {"$regex": search, "$options": "i"}

    # Get all items for transfer suggestion calculations
    all_items = list(inventory_collection.find({}, {"_id": 0}))
    filtered_data = list(inventory_collection.find(query, {"_id": 0}))
    
    result = [smart_inventory_logic(item, all_items) for item in filtered_data]
    return result


@router.get("/category-performance")
def category_performance():
    """Get category-wise inventory and sales analytics."""
    items = list(inventory_collection.find({}, {"_id": 0}))
    
    category_stats = {}
    for item in items:
        cat = item.get("category", "Uncategorized")
        if cat not in category_stats:
            category_stats[cat] = {
                "totalStock": 0,
                "totalValue": 0,
                "itemCount": 0,
                "criticalItems": 0,
            }
        category_stats[cat]["totalStock"] += item.get("stockQuantity", 0)
        category_stats[cat]["totalValue"] += item.get("costPrice", 0) * item.get("stockQuantity", 0)
        category_stats[cat]["itemCount"] += 1
        if item.get("stockStatus") == "Critical":
            category_stats[cat]["criticalItems"] += 1
    
    return category_stats


@router.get("/alerts")
def get_alerts():
    """Get real-time alerts for critical inventory situations."""
    all_items = list(inventory_collection.find({}, {"_id": 0}))
    alerts = []
    
    for item in all_items:
        stock = item.get("stockQuantity", 0)
        status = item.get("stockStatus")
        product_id = item.get("productId")
        dead_stock = detect_dead_stock(product_id)
        expiry = item.get("expiryStatus")
        
        if status == "Critical":
            alerts.append({
                "type": "Low Stock",
                "productId": product_id,
                "branchId": item.get("branchId"),
                "severity": "Critical",
                "message": f"Stock critically low: {stock} units",
            })
        
        if dead_stock:
            alerts.append({
                "type": "Dead Stock",
                "productId": product_id,
                "branchId": item.get("branchId"),
                "severity": "High",
                "message": "No sales in 30 days. Consider discount.",
            })
        
        if expiry == "Expiring Soon":
            alerts.append({
                "type": "Expiry Alert",
                "productId": product_id,
                "branchId": item.get("branchId"),
                "severity": "Critical",
                "message": "Product expiring within 5 days.",
            })
    
    return alerts
