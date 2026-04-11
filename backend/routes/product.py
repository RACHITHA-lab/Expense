from fastapi import APIRouter, Query, HTTPException
from database import product_collection
from typing import Optional

router = APIRouter()

@router.post("/add-product")
def add_product(data: dict):
    product_collection.insert_one(data)
    return {"message": "Product added"}

@router.get("/products")
def get_products():
    return list(product_collection.find({}, {"_id": 0}))

@router.put("/update-product/{product_id}")
def update_product(product_id: str, data: dict):
    # Professional Update API
    result = product_collection.update_one({"productId": product_id}, {"$set": data})
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product upated successfully"}

@router.delete("/delete-product/{product_id}")
def delete_product(product_id: str):
    # Professional Delete API
    result = product_collection.delete_one({"productId": product_id})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Product not found")
    return {"message": "Product deleted successfully"}
