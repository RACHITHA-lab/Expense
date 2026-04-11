import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error
import pickle
import os

# Create CSV from XLSX if it doesn't exist
if not os.path.exists("prediction_dataset.csv") and os.path.exists("data/prediction.xlsx"):
    print("Converting prediction.xlsx to prediction_dataset.csv...")
    df = pd.read_excel("data/prediction.xlsx")
    df.to_csv("prediction_dataset.csv", index=False)

# Load dataset
data = pd.read_csv("prediction_dataset.csv")

# Features (input)
X = data[[
    "lastWeekSales",
    "lastMonthSales",
    "currentStock"
]]

# Target (output)
y = data["predictedDemand"]

# Split data
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# Train model (better than linear regression)
model = RandomForestRegressor(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate
predictions = model.predict(X_test)
error = mean_absolute_error(y_test, predictions)

print("Model trained successfully")
print("MAE:", error)

# Save model
with open("demand_model.pkl", "wb") as f:
    pickle.dump(model, f)
