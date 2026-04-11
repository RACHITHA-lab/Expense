from fastapi import APIRouter
from database import branch_collection

router = APIRouter()

@router.post("/add-branch")
def add_branch(data: dict):
    branch_collection.insert_one(data)
    return {"message": "Branch added"}

@router.get("/branches")
def get_branches():
    data = list(branch_collection.find({}, {"_id": 0}))
    return data
