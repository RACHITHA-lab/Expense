from fastapi import APIRouter
from database import inventory_collection, sales_collection, orders_collection
from datetime import datetime

router = APIRouter()

# Mock Supplier database for the Decision Engine
# In production, this would be a separate MongoDB collection "suppliers"
MOCK_SUPPLIERS = [
    {"supplierId": "SUP-001", "name": "Global Traders", "leadTimeDays": 5, "reliability": 0.95, "costMultiplier": 1.0},
    {"supplierId": "SUP-002", "name": "FastTrack Logistics", "leadTimeDays": 2, "reliability": 0.88, "costMultiplier": 1.15},
    {"supplierId": "SUP-003", "name": "Eco Retail Supply", "leadTimeDays": 7, "reliability": 0.99, "costMultiplier": 0.9},
]

@router.get("/decisions")
def get_ai_decisions():
    """AI Decision Engine integrating Inventory, Predictions, and Suppliers."""
    inventory = list(inventory_collection.find({}, {"_id": 0}))
    decisions = []

    # Iterate through items to find those needing actions
    for item in inventory:
        stock = item.get("stockQuantity", 0)
        product_id = item.get("productId", "Unknown")
        branch_id = item.get("branchId", "Unknown")
        
        # Determine dynamic reorder level based on predicted demand and lead time
        # This was calculated in smart-inventory but let's re-eval quickly 
        predicted = item.get("predictedDemand", 0)
        if predicted == 0:
            predicted = item.get("lastWeekSales", 50) * 1.1 # Fallback prediction
            
        safety_stock = item.get("safetyStock", 20)
        best_supplier = min(MOCK_SUPPLIERS, key=lambda s: s["leadTimeDays"]) # Default to fastest
        dynamic_reorder_level = int(round((predicted / 7) * best_supplier["leadTimeDays"] + safety_stock))
        
        # 1. Supplier / Restock Selection
        if stock < dynamic_reorder_level:
            # Need to order. Find supplier balancing speed if critically low, or cost if just low
            critical = stock < (dynamic_reorder_level / 2)
            if critical:
                # Need it fast
                chosen_supplier = min(MOCK_SUPPLIERS, key=lambda s: s["leadTimeDays"])
                reason = "Critically low stock. Chose fastest supplier."
            else:
                # Need it cheap but reliable
                chosen_supplier = min(MOCK_SUPPLIERS, key=lambda s: s["costMultiplier"])
                reason = "Stock low. Chose most cost-effective supplier."
                
            qty_to_order = int(predicted - stock + safety_stock)
            if qty_to_order > 0:
                decisions.append({
                    "decisionType": "RESTOCK_SUPPLIER",
                    "productId": product_id,
                    "branchId": branch_id,
                    "action": f"Order {qty_to_order} units from {chosen_supplier['name']}",
                    "reason": reason,
                    "metrics": {"leadTime": chosen_supplier["leadTimeDays"], "costMulti": chosen_supplier["costMultiplier"]},
                    "priority": "High" if critical else "Medium"
                })

        # 2. Transfer Suggestion Logic (Decision phase)
        # Assuming other branches have > 100 surplus and we are < 30
        if stock < 30:
            for other in inventory:
                if other.get("productId") == product_id and other.get("branchId") != branch_id:
                    if other.get("stockQuantity", 0) > 100:
                        decisions.append({
                            "decisionType": "BRANCH_TRANSFER",
                            "productId": product_id,
                            "branchId": branch_id,
                            "action": f"Request transfer from {other.get('branchId')}",
                            "reason": f"Source branch has surplus ({other.get('stockQuantity')}). Cheaper than ordering new.",
                            "priority": "Medium"
                        })
                        break # One transfer recommendation per low item
                        
    return {"decisions": decisions}

@router.post("/execute-decision")
def execute_decision(decision: dict):
    decision_type = decision.get("decisionType")
    product_id = decision.get("productId")
    branch_id = decision.get("branchId")
    
    if not product_id or not branch_id or not decision_type:
         return {"success": False, "message": "Invalid decision payload"}

    if decision_type == "RESTOCK_SUPPLIER":
        qty = 50
        import re
        match = re.search(r"Order (\d+)", decision.get("action", ""))
        if match:
            qty = int(match.group(1))
            
        order_record = {
             "productId": product_id,
             "branchId": branch_id,
             "quantity": qty,
             "status": "APPROVED",
             "supplier": decision.get("reason", "Unknown Supplier Algorithm"),
             "timestamp": str(datetime.now())
        }
        orders_collection.insert_one(order_record)
        
        inventory_collection.update_one(
             {"productId": product_id, "branchId": branch_id},
             {"$inc": {"stockQuantity": qty}}
        )
        return {"success": True, "message": f"Successfully ordered {qty} units and updated virtual stock!"}
        
    elif decision_type == "BRANCH_TRANSFER":
        source_branch = None
        import re
        # Try to find branch code like B001 etc.
        match = re.search(r"from (B\w+)", decision.get("action", ""))
        if match:
            source_branch = match.group(1)
        else:
             # Fallback: parse from generic text "Request transfer from X"
             words = decision.get("action", "").split()
             if len(words) > 0:
                 source_branch = words[-1]
                 
        if not source_branch:
             return {"success": False, "message": "Could not determine source branch"}
             
        qty = 50 # Default transfer block
        
        res1 = inventory_collection.update_one(
             {"productId": product_id, "branchId": source_branch},
             {"$inc": {"stockQuantity": -qty}}
        )
        if res1.matched_count == 0:
             return {"success": False, "message": "Source branch not found or empty"}
             
        inventory_collection.update_one(
             {"productId": product_id, "branchId": branch_id},
             {"$inc": {"stockQuantity": qty}}
        )
        
        return {"success": True, "message": f"Successfully transferred {qty} units from {source_branch}."}
        
    return {"success": False, "message": "Unknown decision type"}
