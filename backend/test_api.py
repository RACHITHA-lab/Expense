import urllib.request
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def post_json(endpoint, data):
    url = f"{BASE_URL}{endpoint}"
    req = urllib.request.Request(url, method="POST", data=json.dumps(data).encode('utf-8'))
    req.add_header("Content-Type", "application/json")
    try:
        response = urllib.request.urlopen(req)
        return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return f"Error: {e}"

def get_json(endpoint):
    url = f"{BASE_URL}{endpoint}"
    try:
        response = urllib.request.urlopen(url)
        return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        return f"Error: {e}"

print("🚀 Starting module-by-module testing sequence...\n")

# 1. Branch
print("🏢 1. TEST BRANCH API")
print("➤ Add Branch:", post_json("/add-branch", {
  "branchId": "B101",
  "branchName": "DMart Whitefield",
  "city": "Bangalore",
  "managerName": "Ravi"
}))
print("➤ Get Branches:", get_json("/branches"))
print()

# 2. Product
print("🛒 2. TEST PRODUCT API")
print("➤ Add Product:", post_json("/add-product", {
  "productId": "P101",
  "productName": "Rice",
  "category": "Grocery",
  "price": 50
}))
print("➤ Get Products:", get_json("/products"))
print()

# 3. Inventory
print("📦 3. TEST INVENTORY")
print("➤ Add Inventory:", post_json("/update-stock", {
  "inventoryId": "I101",
  "branchId": "B101",
  "productId": "P101",
  "stockQuantity": 10,
  "minStockLevel": 20
}))
print("➤ Get Inventory:", get_json("/inventory"))
print()

# 4. Sales
print("💰 4. TEST SALES")
print("➤ Add Sale:", post_json("/add-sale", {
  "saleId": "S101",
  "branchId": "B101",
  "productId": "P101",
  "quantity": 3,
  "totalAmount": 150
}))
print("➤ Get Sales:", get_json("/sales"))
print()

# 5. Expense
print("💸 5. TEST EXPENSE")
print("➤ Add Expense:", post_json("/add-expense", {
  "expenseId": "E101",
  "branchId": "B101",
  "amount": 120000
}))
print("➤ Get Expenses:", get_json("/expenses"))
print()

# 6. Analytics
print("📊 6. TEST ANALYTICS")
print("➤ Get Analytics:", get_json("/analytics"))
print()

# 7. Alerts
print("🔔 7. TEST ALERTS")
print("➤ Get Alerts:", get_json("/alerts"))
print()

print("✅ TEST COMPLETE!")
