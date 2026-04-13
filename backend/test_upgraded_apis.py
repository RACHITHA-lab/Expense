import requests

BASE_URL = "http://127.0.0.1:8000"
product_id = "P1005"

print("\n--- SMART INVENTORY ---\n")
res1 = requests.get(f"{BASE_URL}/smart-inventory/{product_id}")
print(res1.json())

print("\n--- ALERTS ---\n")
res2 = requests.get(f"{BASE_URL}/alerts/{product_id}")
print(res2.json())
