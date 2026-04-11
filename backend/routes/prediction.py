from fastapi import APIRouter
from utils.predict import predict_demand
from models.schemas import PredictionInput
import os
import pickle

router = APIRouter()

model_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ml", "demand_model.pkl")
try:
    with open(model_path, "rb") as f:
        model = pickle.load(f)
except Exception:
    model = None

@router.post("/forecast")
def forecast(data: PredictionInput):
    predicted = predict_demand(
        model,
        data.lastWeekSales,
        data.lastMonthSales,
        data.currentStock
    )

    return {
        "predictedDemand": predicted,
        "action": "Restock" if predicted > data.currentStock else "Stock OK"
    }
