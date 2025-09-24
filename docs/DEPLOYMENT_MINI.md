# HSEG Deployment (Minimal Guide)

This is a quick, minimal set of steps to run the HSEG API and frontend with pre‑trained models.

## Prerequisites
- Docker and Docker Compose installed
- Trained model artifacts present in `app/models/trained/`:
  - `individual_risk_model.pkl`
  - `text_risk_classifier.pkl`
  - `organizational_risk_model.pkl`

If you need to train models locally first:
```
python scripts/train_all_from_final_dataset.py
```

## Option A: Run with Docker (simple)

### API
```
docker build -t hseg-ai-api .
docker run -p 8000:8000 hseg-ai-api
```
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs

### Frontend
```
cd frontend
docker build -t hseg-frontend .
docker run -p 3000:3000 -e REACT_APP_API_URL=http://localhost:8000 hseg-frontend
```
- Portal: http://localhost:3000

## Option B: Local dev (no Docker)

### Backend
```
pip install -r requirements.txt
uvicorn app.api.main:app --host 0.0.0.0 --port 8000
```
- Health: http://localhost:8000/health
- Docs: http://localhost:8000/docs

### Frontend
```
cd frontend
npm install
# Windows PowerShell
$env:REACT_APP_API_URL = 'http://localhost:8000'
npm start
```
- Portal: http://localhost:3000

## Notes
- Database defaults to SQLite at `./database/hseg_database.db`.
- For demos, SQLite is sufficient; for production use Postgres (see `docker-compose.yml`).
- Only core files are kept for deployment; additional docs/legacy/tests are in `dump/`. 
