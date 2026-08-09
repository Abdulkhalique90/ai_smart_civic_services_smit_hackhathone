from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from app.schemas import ComplaintCreate, ComplaintOut, ComplaintUpdate
from app.services.ai_analyzer import AIAnalyzer
from app.db.database import init_db, save_complaint, list_complaints, update_complaint, get_stats
import json
from datetime import datetime
import os

app = FastAPI(title="AI Smart Civic Services - API")

static_dir = os.path.join(os.path.dirname(__file__), 'static')
app.mount('/static', StaticFiles(directory=static_dir), name='static')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

ai = AIAnalyzer()


@app.on_event("startup")
def startup():
    init_db()


@app.post("/complaints", response_model=ComplaintOut)
def create_complaint(data: ComplaintCreate):
    text = data.description
    ai_result = ai.analyze(text)
    record = {
        "description": data.description,
        "category": ai_result.get("category"),
        "priority": ai_result.get("priority"),
        "location": data.location or "",
        "date": datetime.utcnow().isoformat(),
        "status": "Open",
        "assigned_department": "",
        "recommended_department": ai_result.get("recommended_department"),
        "ai_output": json.dumps(ai_result),
        "resolved_date": None,
    }
    saved = save_complaint(record)
    if not saved:
        raise HTTPException(status_code=500, detail="Unable to save complaint")
    out = {**record, "complaint_id": saved}
    return out


@app.get("/complaints")
def get_complaints(category: str = None, priority: str = None, status: str = None, assigned_department: str = None, location: str = None, search: str = None):
    rows = list_complaints({
        'category': category,
        'priority': priority,
        'status': status,
        'assigned_department': assigned_department,
        'location': location,
        'search': search,
    })
    return rows


@app.put("/complaints/{complaint_id}")
def patch_complaint(complaint_id: int, updates: ComplaintUpdate):
    success = update_complaint(complaint_id, updates.dict())
    if not success:
        raise HTTPException(status_code=404, detail="Complaint not found or no valid updates")
    return {"complaint_id": complaint_id, "updated": True}


@app.get("/stats")
def stats():
    return get_stats()


@app.get("/")
def admin_ui():
    return FileResponse(os.path.join(static_dir, 'admin.html'))
