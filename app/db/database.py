import sqlite3
import os
from typing import Dict, List
from datetime import datetime
import statistics

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'data', 'complaints.db')


def _ensure_column(conn, table: str, column: str, col_type: str = 'TEXT'):
    cur = conn.cursor()
    cur.execute(f'PRAGMA table_info({table})')
    cols = [row[1] for row in cur.fetchall()]
    if column not in cols:
        cur.execute(f'ALTER TABLE {table} ADD COLUMN {column} {col_type}')


def init_db():
    db_dir = os.path.dirname(DB_PATH)
    os.makedirs(db_dir, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
    CREATE TABLE IF NOT EXISTS complaints (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        description TEXT,
        category TEXT,
        priority TEXT,
        location TEXT,
        date TEXT,
        status TEXT,
        assigned_department TEXT,
        recommended_department TEXT,
        ai_output TEXT,
        resolved_date TEXT
    )
    ''')
    conn.commit()
    _ensure_column(conn, 'complaints', 'resolved_date', 'TEXT')
    _ensure_column(conn, 'complaints', 'recommended_department', 'TEXT')
    conn.commit()
    conn.close()


def save_complaint(record: Dict) -> int:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        '''INSERT INTO complaints (description, category, priority, location, date, status, assigned_department, recommended_department, ai_output, resolved_date)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
        (record.get('description'), record.get('category'), record.get('priority'), record.get('location'), record.get('date'), record.get('status'), record.get('assigned_department'), record.get('recommended_department'), record.get('ai_output'), record.get('resolved_date'))
    )
    conn.commit()
    cid = cur.lastrowid
    conn.close()
    return cid


def list_complaints(filters: Dict = None) -> List[Dict]:
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    query = 'SELECT * FROM complaints'
    params = []
    if filters:
        clauses = []
        if filters.get('category'):
            clauses.append('category = ?')
            params.append(filters['category'])
        if filters.get('priority'):
            clauses.append('priority = ?')
            params.append(filters['priority'])
        if filters.get('status'):
            clauses.append('status = ?')
            params.append(filters['status'])
        if filters.get('assigned_department'):
            clauses.append('assigned_department = ?')
            params.append(filters['assigned_department'])
        if filters.get('location'):
            clauses.append('location LIKE ?')
            params.append(f"%{filters['location']}%")
        if filters.get('search'):
            clauses.append('(description LIKE ? OR location LIKE ?)')
            params.append(f"%{filters['search']}%")
            params.append(f"%{filters['search']}%")
        if clauses:
            query += ' WHERE ' + ' AND '.join(clauses)
    query += ' ORDER BY id DESC'
    cur.execute(query, params)
    rows = cur.fetchall()
    out = []
    for r in rows:
        out.append({
            'complaint_id': r['id'],
            'description': r['description'],
            'category': r['category'],
            'priority': r['priority'],
            'location': r['location'],
            'date': r['date'],
            'status': r['status'],
            'assigned_department': r['assigned_department'],
            'recommended_department': r['recommended_department'],
            'ai_output': r['ai_output'],
            'resolved_date': r['resolved_date'],
        })
    conn.close()
    return out


def update_complaint(complaint_id: int, updates: Dict) -> bool:
    if not updates:
        return False
    allowed = ['status', 'assigned_department', 'location']
    set_clauses = []
    params = []
    for key in allowed:
        if key in updates and updates[key] is not None:
            set_clauses.append(f'{key} = ?')
            params.append(updates[key])
    if 'status' in updates and updates['status'] == 'Resolved':
        set_clauses.append('resolved_date = ?')
        params.append(datetime.utcnow().isoformat())
    if not set_clauses:
        return False
    params.append(complaint_id)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(f'UPDATE complaints SET {", ".join(set_clauses)} WHERE id = ?', params)
    conn.commit()
    updated = cur.rowcount > 0
    conn.close()
    return updated


def get_stats() -> Dict:
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    stats = {}
    cur.execute('SELECT COUNT(*) FROM complaints')
    stats['total_complaints'] = cur.fetchone()[0]
    for field in ['category', 'priority', 'status', 'assigned_department', 'recommended_department']:
        cur.execute(f'SELECT {field}, COUNT(*) FROM complaints GROUP BY {field} ORDER BY COUNT(*) DESC')
        stats[f'{field}_distribution'] = [{row[0] or 'Unknown': row[1]} for row in cur.fetchall()]
    cur.execute('SELECT date, resolved_date FROM complaints WHERE status = ? AND resolved_date IS NOT NULL', ('Resolved',))
    rows = cur.fetchall()
    durations = []
    for created, resolved in rows:
        try:
            start = datetime.fromisoformat(created)
            end = datetime.fromisoformat(resolved)
            hours = (end - start).total_seconds() / 3600.0
            if hours >= 0:
                durations.append(hours)
        except Exception:
            continue
    if durations:
        stats['resolution_count'] = len(durations)
        stats['resolution_hours'] = {
            'mean': round(statistics.mean(durations), 2),
            'median': round(statistics.median(durations), 2),
            'mode': round(statistics.mode(durations), 2) if len(set(durations)) > 1 else round(durations[0], 2),
            'min': round(min(durations), 2),
            'max': round(max(durations), 2),
            'range': round(max(durations) - min(durations), 2),
            'variance': round(statistics.variance(durations), 2) if len(durations) > 1 else 0.0,
            'stdev': round(statistics.stdev(durations), 2) if len(durations) > 1 else 0.0,
        }
    else:
        stats['resolution_count'] = 0
        stats['resolution_hours'] = {}
    conn.close()
    return stats
