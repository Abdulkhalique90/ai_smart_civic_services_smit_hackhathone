import csv
import json
import os
from datetime import datetime
from app.db.database import init_db, save_complaint

BASE_DIR = os.path.dirname(os.path.dirname(__file__))

if __name__ == '__main__':
    init_db()
    data_path = os.path.join(BASE_DIR, 'app', 'data', 'sample_complaints.csv')
    with open(data_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            record = {
                'description': row['description'],
                'category': None,
                'priority': None,
                'location': row.get('location', ''),
                'date': datetime.utcnow().isoformat(),
                'status': 'Open',
                'assigned_department': '',
                'recommended_department': None,
                'ai_output': json.dumps({}),
                'resolved_date': None,
            }
            save_complaint(record)
    print('Seeded complaints from', data_path)
