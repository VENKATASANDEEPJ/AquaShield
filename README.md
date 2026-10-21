# AquaShield AI

**Urban Water Intelligence Dashboard**

AquaShield AI is a data-driven urban water intelligence platform for exploring historical rainfall data, analyzing custom datasets, and understanding available city-level data coverage.

## Live Deployment

- **Live Dashboard:** https://aqua-shield-orcin.vercel.app
- **Backend API:** https://aquashield-hon1.onrender.com
- **API Health Check:** https://aquashield-hon1.onrender.com/api/health

## Tech Stack

### Frontend

- **React 19** — User interface
- **Vite 8** — Frontend development server and build tool
- **JavaScript / JSX**
- **Recharts** — Charts and data visualization
- **CSS** — Custom styling in `styles.css`
- **Vercel** — Frontend deployment
- **Configuration:** `frontend/package.json`

### Backend

- **Python 3.10+**
- **FastAPI** — REST API framework
- **Uvicorn** — ASGI server
- **Pydantic / FastAPI validation** — Request and response validation
- **CORS middleware** — Cross-origin communication with the Vercel frontend
- **python-multipart** — CSV and file upload handling
- **Render** — Backend deployment
- **Entrypoint:** `backend/app/main.py`

### Data Processing and Analysis

- **Pandas** — CSV processing, cleaning, profiling, and descriptive analysis
- **NumPy** — Numerical operations
- **scikit-learn** — Data science dependency; no supervised ML or flood-prediction model is currently enabled
- **Open-Meteo Historical Weather API** — Historical rainfall data using ERA5 reanalysis estimates
- **Data ingestion script:** `scripts/ingest_rainfall.py`

### Database and Persistence

- **SQLAlchemy** — ORM and database abstraction
- **SQLite** — Default local database
- **PostgreSQL** — Supported through `DATABASE_URL`
- **psycopg** — PostgreSQL database driver

Experiment metadata and analysis summaries are persisted. Uploaded CSV row data is processed in memory.

### Testing

- **pytest** — Backend testing
- **FastAPI TestClient**
- **httpx** — HTTP client and test support
- **Test file:** `backend/tests/test_api.py`

## Features

- City selection for six cities: Hyderabad, Chennai, Mumbai, Bengaluru, Delhi, and Kolkata.
- Historical rainfall exploration and visualization.
- Rainfall summaries, daily records, and heavy-rain-day statistics.
- CSV dataset upload, profiling, cleaning, and analysis.
- Export support for dataset analysis results.
- Experiment metadata and analysis history.
- Data-source coverage indicators and transparent limitations.

## Data Limitations

- Rainfall values are ERA5 reanalysis estimates, not direct rain-gauge observations.
- Rainfall coverage uses city-point coordinates and does not represent ward-level variation.
- Waterlogging, road access, and water-quality data sources are not currently configured.
- The application does not currently provide an operational flood-prediction model.

## Running Locally

### 1. Clone the repository

```bash
git clone https://github.com/VENKATASANDEEPJ/AquaShield.git
cd AquaShield
```

### 2. Start the backend

Follow the dependencies and configuration defined in the `backend` directory. Start the FastAPI application using the project's configured Uvicorn command.

### 3. Start the frontend

```bash
cd frontend
npm install
npm run dev
```

Configure the frontend API base URL to point to your local backend when running locally.

## Project Structure

```text
AquaShield/
├── backend/
│   ├── app/
│   │   └── main.py
│   └── tests/
│       └── test_api.py
├── frontend/
│   ├── src/
│   ├── package.json
│   └── styles.css
├── data/
├── docs/
├── models/
├── notebooks/
├── scripts/
│   └── ingest_rainfall.py
├── render.yaml
└── README.md
```

## Future Improvements

- Integrate verified waterlogging and flood incident datasets.
- Add road-disruption and water-quality data sources.
- Explore and evaluate suitable ML models using validated datasets.
- Improve spatial coverage beyond city-point rainfall estimates.

## Author

**J. Venkata Sandeep**

GitHub: https://github.com/VENKATASANDEEPJ

