from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")
db = client["dmart_db"]

branch_collection = db["branches"]
product_collection = db["products"]
inventory_collection = db["inventory"]
sales_collection = db["sales"]
expense_collection = db["expenses"]
