# AI Smart Civic Services — FastAPI scaffold

Minimal FastAPI scaffold with a simple `AIAnalyzer`, SQLite storage, and a training script to generate a tiny classifier.

Quick start

1. Create a virtualenv and install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
```

2. Train the example classifier (optional, otherwise analyzer uses rule-based fallback):

```bash
pip install scikit-learn
python scripts/train_model.py
```

3. Run the FastAPI app:

```bash
uvicorn app.main:app --reload --port 8000
```

4. Run the Streamlit dashboard in a separate terminal:

```bash
streamlit run dashboard.py
```

### Useful API calls

- `POST /complaints` with JSON:
  ```json
  {
    "description": "There is a large water leak near the main road.",
    "location": "Main Road"
  }
  ```
- `GET /complaints` with optional query parameters: `category`, `priority`, `status`, `assigned_department`, `location`, `search`
- `PUT /complaints/{complaint_id}` to update `status`, `assigned_department`, or `location`
- `GET /stats` to fetch counts and distributions

`POST /complaints` also stores an AI recommendation field, `recommended_department`, so administrators can see which service team is most appropriate for a complaint.

3. Run the FastAPI app:

```bash
uvicorn app.main:app --reload --port 8000
```

API endpoints

- `POST /complaints` — submit complaint JSON: `{ "description": "...", "location": "..." }`
- `GET /complaints` — list saved complaints

Files of interest

- [app/main.py](app/main.py)
- [app/services/ai_analyzer.py](app/services/ai_analyzer.py)
- [app/db/database.py](app/db/database.py)
- [scripts/train_model.py](scripts/train_model.py)
