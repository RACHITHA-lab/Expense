from fastapi import APIRouter
import csv
from io import StringIO
from fastapi.responses import Response
from database import sales_collection, expense_collection, inventory_collection

router = APIRouter()

@router.get("/export-csv")
def export_csv(report_type: str = "sales"):
    """
    Exports collection data directly to CSV for external Analytics tools (PowerBI, Excel).
    Bonus Feature.
    """
    output = StringIO()
    writer = csv.writer(output)
    
    if report_type == "sales":
        data = list(sales_collection.find({}, {"_id": 0}))
        if data:
            writer.writerow(data[0].keys())
            for row in data:
                writer.writerow(row.values())
                
    elif report_type == "expenses":
        data = list(expense_collection.find({}, {"_id": 0}))
        if data:
            writer.writerow(data[0].keys())
            for row in data:
                writer.writerow(row.values())

    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={report_type}_report.csv"}
    )
