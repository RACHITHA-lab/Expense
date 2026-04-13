from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from routes import (
    branch, product, inventory, sales, expense, 
    analytics, alerts, prediction, ranking, dashboard, auth, export, supplier, decisions
)

app = FastAPI(title="DMart API + ML Backend")

# Maintain CORS for React integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Core CRUD
app.include_router(branch.router)
app.include_router(product.router)
app.include_router(inventory.router)
app.include_router(sales.router)
app.include_router(expense.router)

# Advanced Views
app.include_router(analytics.router)
app.include_router(alerts.router)
app.include_router(prediction.router)
app.include_router(ranking.router)
app.include_router(dashboard.router)
app.include_router(decisions.router)

# Auth
app.include_router(auth.router)

# Bonus Features
app.include_router(export.router)
app.include_router(supplier.router)

@app.get("/")
def home():
    return {"message": "DMart Full-Stack API Running Perfectly 🚀"}
