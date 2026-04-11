from pydantic import BaseModel
from typing import Optional

class Sale(BaseModel):
    productId: str
    quantity: int
    totalAmount: float
    branchId: Optional[str] = None
    saleId: Optional[str] = None

class PredictionInput(BaseModel):
    lastWeekSales: float
    lastMonthSales: float
    currentStock: float

class Login(BaseModel):
    email: str
    password: str
