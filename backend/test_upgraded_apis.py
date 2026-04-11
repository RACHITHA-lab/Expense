import urllib.request
import json

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

print("🚀 RUNNING FINAL UPGRADE TESTS...\n")

# 1. Forecast
print("🔮 1. TEST Forecast API")
print(post_json("/forecast", {
  "lastWeekSales": 120.0,
  "lastMonthSales": 500.0,
  "currentStock": 80.0
}))
print()

# 2. Dashboard
print("📊 2. TEST Dashboard Summary")
print(get_json("/dashboard-summary"))
print()

# 3. Branch Ranking
print("🏆 3. TEST Branch Ranking")
print(get_json("/branch-ranking"))
print()

# 4. Alerts
print("🔔 4. TEST Alerts")
print(get_json("/alerts"))
print()

# 5. Analytics
print("📊 5. TEST Analytics")
print(get_json("/analytics"))
print()

# 6. Login
print("🔐 6. TEST Login")
print(post_json("/login", {
  "email": "admin@gmail.com",
  "password": "1234"
}))
print()

# 7. Inventory ML Check
print("🧠 7. TEST Inventory ML")
print(get_json("/inventory"))
print()

print("✅ UPGRADE TEST COMPLETE!")
