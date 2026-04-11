def predict_demand(model, last_week_sales, last_month_sales, current_stock):
    if not model:
        return 0
    try:
        prediction = model.predict([[
            last_week_sales,
            last_month_sales,
            current_stock
        ]])
        return float(prediction[0])
    except Exception as e:
        print(f"Prediction error: {e}")
        return 0
