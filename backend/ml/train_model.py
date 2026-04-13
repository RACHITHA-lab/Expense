import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pickle
import os

# Generate new dynamic dataset simulating retail environment in India
def generate_mock_data(num_records=5000):
    np.random.seed(42)
    last_week_sales = np.random.randint(10, 500, num_records)
    last_month_sales = last_week_sales * 4 + np.random.randint(-50, 150, num_records)
    current_stock = np.random.randint(5, 1000, num_records)
    
    # Seasonality: 1=Winter, 2=Spring, 3=Summer, 4=Monsoon/Autumn
    seasonality = np.random.randint(1, 5, num_records)
    
    # Day of week: 0=Monday, 6=Sunday
    day_of_week = np.random.randint(0, 7, num_records)
    
    # Festival effect: 1 if festival (Diwali, Holi, etc.), 0 otherwise
    # ~10% chance of festival days
    festival_effect = np.random.choice([0, 1], num_records, p=[0.9, 0.1])
    
    # Target: predictedDemand
    # Logic: Base demand related to past sales, boosted by festivals and weekends
    predicted_demand = last_week_sales * 1.1
    predicted_demand += np.where(day_of_week >= 5, 20, 0) # Weekend boost
    predicted_demand += np.where(festival_effect == 1, last_week_sales * 0.8, 0) # Massive festival boost
    
    # Slight season variations
    season_mult = np.array([1.1, 1.0, 1.2, 0.9])
    predicted_demand = predicted_demand * season_mult[seasonality - 1]
    
    df = pd.DataFrame({
        "lastWeekSales": last_week_sales,
        "lastMonthSales": last_month_sales,
        "currentStock": current_stock,
        "seasonality": seasonality,
        "day_of_week": day_of_week,
        "festival_effect": festival_effect,
        "predictedDemand": np.round(predicted_demand).astype(int)
    })
    
    df.to_csv("prediction_dataset.csv", index=False)
    print("Generated dynamic dataset with extra AI features.")

if not os.path.exists("prediction_dataset.csv"):
    generate_mock_data()
else:
    # Always regenerate for this demo to ensure new features exist
    generate_mock_data()

# Load dataset
data = pd.read_csv("prediction_dataset.csv")

# Features (input)
X = data[[
    "lastWeekSales",
    "lastMonthSales",
    "currentStock",
    "seasonality",
    "day_of_week",
    "festival_effect"
]]

# Target (output)
y = data["predictedDemand"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model (RandomForest handles non-linear patterns like festivals well)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
error = mean_absolute_error(y_test, predictions)

print("Model trained successfully with Advanced Enterprise AI Features!")
print("Mean Absolute Error (MAE):", round(error, 2))

# Save model
model_path = os.path.join(os.path.dirname(__file__), "demand_model.pkl")
with open(model_path, "wb") as f:
    pickle.dump(model, f)

