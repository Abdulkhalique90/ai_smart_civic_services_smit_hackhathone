import csv
import json
import os
import sys
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

from app.db.database import init_db, save_complaint

BASE_DIR = Path(__file__).resolve().parent.parent
CSV_PATH = BASE_DIR / 'Complaint_Attorney_2023_CDMX.csv'

PRIORITY_MAP = {
    'HOMICIDIO': 'Critical',
    'VIOLACION': 'Critical',
    'FEMINICIDIO': 'Critical',
    'ROBO': 'High',
    'LESIONES': 'Medium',
    'AMENAZAS': 'Medium',
    'FRAUDE': 'Medium',
    'DAÑO': 'Low',
    'PERDIDA DE LA VIDA': 'Critical',
}


def make_description(row: dict) -> str:
    delito = row.get('Delito') or row.get('Categoria') or 'Reported incident'
    location = row.get('colonia_datos') or row.get('alcaldia_hechos') or row.get('municipio_hechos') or ''
    fecha = row.get('FechaHecho') or row.get('FechaInicio') or ''
    hora = row.get('HoraHecho') or row.get('HoraInicio') or ''
    pieces = [delito]
    if location:
        pieces.append(f'at {location}')
    if fecha:
        pieces.append(f'on {fecha}')
    if hora:
        pieces.append(f'at {hora}')
    return ' '.join(pieces)


def make_location(row: dict) -> str:
    location = row.get('colonia_datos') or row.get('fgj_colonia_registro') or ''
    area = row.get('alcaldia_hechos') or row.get('municipio_hechos') or ''
    if location and area:
        return f"{location}, {area}"
    if location:
        return location
    if area:
        return area
    lat = row.get('latitud')
    lon = row.get('longitud')
    if lat and lon and lat != 'NA' and lon != 'NA':
        return f"{lat},{lon}"
    return 'Unknown'


def map_priority(delito: str) -> str:
    if not delito:
        return 'Medium'
    key = delito.upper()
    for pattern, priority in PRIORITY_MAP.items():
        if pattern in key:
            return priority
    return 'Medium'


def load_cdmx_csv(path: Path, limit: int = None):
    with path.open(newline='', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader, start=1):
            if limit and idx > limit:
                break
            yield row


def import_complaints(limit: int = None, start: int = 1):
    init_db()

    total = 0
    for idx, row in enumerate(load_cdmx_csv(CSV_PATH, limit=None), start=1):
        if idx < start:
            continue
        if limit and total >= limit:
            break

        description = make_description(row)
        location = make_location(row)
        priority = map_priority(row.get('Delito') or row.get('Categoria', ''))
        date = row.get('FechaHecho') or row.get('FechaInicio') or datetime.utcnow().date().isoformat()

        record = {
            'description': description,
            'category': row.get('Categoria') or row.get('Delito'),
            'priority': priority,
            'location': location,
            'date': date,
            'status': 'Open',
            'assigned_department': '',
            'recommended_department': None,
            'ai_output': json.dumps({
                'source': 'CDMX dataset',
                'idCarpeta': row.get('idCarpeta'),
                'delito': row.get('Delito'),
                'categoria': row.get('Categoria'),
            }),
            'resolved_date': None,
        }
        save_complaint(record)
        total += 1
        if total % 100 == 0:
            print(f'Imported {total} rows...')

    print(f'Imported {total} complaint records from {CSV_PATH.name}')


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Import CDMX complaint dataset into the civic service app database')
    parser.add_argument('--limit', type=int, default=None, help='Maximum number of rows to import')
    parser.add_argument('--start', type=int, default=1, help='Row index to begin importing from (1-based)')
    args = parser.parse_args()

    import_complaints(limit=args.limit, start=args.start)
