# AgroScan

AgroScan is a full-stack crop disease advisory platform built with FastAPI and a browser-based frontend. It predicts crop disease from leaf images and provides treatment guidance, weather cautions, product links, history, and location-aware insights.

## Features

- Leaf image disease prediction using a hybrid CNN pipeline
- Treatment recommendations and step-by-step guidance
- Weather and forecast risk checks for a location
- Alert generation based on disease + weather context
- Voice advisory generation
- Scan history and hotspot analytics
- Multi-page frontend (scan, dashboard, advisory, library)

## Tech Stack

### Backend

- Python
- FastAPI
- TensorFlow / Keras
- MongoDB (PyMongo)
- OpenWeather integration

### Frontend

- HTML
- CSS
- JavaScript

## Project Structure

```text
AgroScan/
  backend/
    app.py
    main.py
    database.py
    requirements.txt
    .env.example
    model/
    static/
    utils/
  frontend/
    index.html
    home.html
    dashboard.html
    advisory.html
    library.html
    scan.js
    app.js
    config.js
    style.css
```

## Prerequisites

- Python 3.10 recommended (TensorFlow 2.12 compatibility)
- MongoDB instance (local or cloud)
- OpenWeather API key

## Backend Setup

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

Create environment file:

```powershell
Copy-Item .env.example .env
```

Update `.env` values:

- `OPENWEATHER_API_KEY`
- `MONGO_URL`
- `MONGO_DB_NAME`
- `CORS_ORIGINS`

## Run Backend

Option 1:

```powershell
cd backend
python main.py
```

Option 2:

```powershell
cd backend
uvicorn app:app --reload --host 127.0.0.1 --port 8000
```

Backend URLs:

- API base: `http://127.0.0.1:8000`
- Swagger docs: `http://127.0.0.1:8000/docs`

## Run Frontend

From project root:

```powershell
cd frontend
python -m http.server 5500
```

Open:

- `http://127.0.0.1:5500/index.html`

The frontend defaults to backend API:

- `http://127.0.0.1:8000` (configured in `frontend/config.js`)

## Main API Endpoints

- `GET /`
- `POST /predict`
- `GET /history/{user_id}`
- `GET /weather/{location}`
- `GET /weather?location=...`
- `GET /forecast-risk/{location}`
- `GET /analytics/hotspots/{user_id}`
- `GET /detect-location`

## Dataset

This project uses a multi-crop disease image dataset for training and validation. The dataset is not committed to this repository due to size.

## Notes

- Do not commit real secrets in `.env`.
- Generated audio files under `backend/static/voice_*.mp3` should generally remain ignored unless intentionally needed.
