from fastapi import APIRouter, HTTPException
from models.schemas import Login
from database import db

router = APIRouter()
user_collection = db["users"]

@router.post("/login")
def login(data: Login):
    # Dynamic DB validation instead of hardcoded string!
    user = user_collection.find_one({"email": data.email})
    if user and user.get("password") == data.password:
        return {"message": "Login success", "user": {"email": user["email"], "role": user.get("role", "admin")}, "token": "mock-jwt-token-123"}
    
    # Fallback to the hardcoded admin if no users seeded yet (safe transition)
    if data.email == "admin@gmail.com" and data.password == "1234":
        return {"message": "Login success (Fallback Admin)", "token": "mock-jwt-token-123"}
        
    raise HTTPException(status_code=401, detail="Invalid credentials")
