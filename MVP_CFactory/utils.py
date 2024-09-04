import csv
import pandas as pd

def export_to_csv(queryset, filename):
    if not queryset:
        return  # No data to export

    with open(filename, mode='w', newline='') as file:
        writer = csv.writer(file)
        headers = [column.name for column in queryset[0].__table__.columns]
        writer.writerow(headers)
        for record in queryset:
            writer.writerow([getattr(record, column) for column in headers])

def generate_production_report():
    from models import session, Fabrication
    productions = session.query(Fabrication).all()
    total_production = sum([p.quantite for p in productions])
    return f"Total Production: {total_production} kg"
