import pandas as pd

def predict_demand(model, last_week_sales, last_month_sales, current_stock, seasonality=1, day_of_week=0, festival_effect=0):
    if not model:
        return 0
    try:
        input_data = pd.DataFrame([[
            last_week_sales,
            last_month_sales,
            current_stock,
            seasonality,
            day_of_week,
            festival_effect
        ]], columns=[
            "lastWeekSales", 
            "lastMonthSales", 
            "currentStock", 
            "seasonality", 
            "day_of_week", 
            "festival_effect"
        ])
        
        prediction = model.predict(input_data)
        return float(prediction[0])
    except Exception as e:
        print(f"Prediction error: {e}")
        return 0
