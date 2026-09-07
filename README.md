# APIx — Real-time Airfare Price Index for India
**Smart India Hackathon 2026 · Problem Statement ID: 26056**  
**Ministry:** Ministry of Statistics and Programme Implementation (MoSPI / NSO)  

---

## 📌 Executive Summary
APIx is an end-to-end automated platform that scrapes real-time domestic airfares across 5 major Indian carriers (IndiGo, Air India, Akasa Air, SpiceJet, Air India Express) and 6 Online Travel Agencies (MakeMyTrip, Yatra, Ixigo, EaseMyTrip, Cleartrip, Goibibo). It cleans and normalises quotes using robust IQR outlier filtering and fare decomposition, computes a DGCA traffic-weighted Laspeyres Airfare Price Index across 5 advance-purchase windows (`T+1` to `T+45`), and serves CPI-ready feeds to MoSPI, the NSO, and the Reserve Bank of India (RBI).

---

## 🚀 Key Features
- **Ethical Multi-Source Scraping**: Full `robots.txt` enforcement, token bucket rate limiter (1 req / 8s), stealth browser context, and User-Agent identification (`APIxBot/1.0`).
- **Data Cleaning & Normalisation**: IQR × 1.5 outlier detection, deduplication across OTAs (keeping lowest fare), and fare decomposition validation.
- **Laspeyres Index Formula**: Incorporates DGCA passenger traffic route weights and advance-purchase booking horizon weights (`T+1`: 10%, `T+7`: 20%, `T+15`: 30%, `T+30`: 25%, `T+45`: 15%).
- **Backtested & Calibrated**: Validated against DGCA published monthly statistics with a Mean Absolute Percentage Error (**MAPE < 8%**).
- **FastAPI Backend**: Async REST API with OpenAPI auto-docs, response caching, and NSO CSV/JSON exports.
- **Ultra-Modern React Dashboard**: Built with React 18, Vite, Tailwind CSS, Recharts, and Canvas/SVG India route network visualizer.

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                       DATA SOURCES                          │
│   IndiGo  Air India  Akasa  SpiceJet  Air India Express     │
│   MakeMyTrip  Yatra  EaseMyTrip  Cleartrip  Ixigo  Goibibo  │
└──────────────────────────────┬──────────────────────────────┘
                               │ Playwright / Stealth Scrapers
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                     SCRAPING ENGINE                         │
│   • Token bucket rate limiter (1 req/8s)                    │
│   • robots.txt compliance checker                           │
│   • Anti-detection spoofing & proxy rotation                │
└──────────────────────────────┬──────────────────────────────┘
                               │ Raw Fare JSON Events
                               ▼
┌─────────────────────────────────────────────────────────────┐
│                 ETL PIPELINE (pandas/numpy)                 │
│   • IQR × 1.5 outlier filtering                             │
│   • Multi-source flight deduplication                       │
│   • Fare decomposition (Base + Taxes + UDF + Fee)           │
└──────────────────────────────┬──────────────────────────────┘
                               │ Cleaned Data
                               ▼
┌─────────────────────────────────────────────────────────────┐
│             STORAGE (TimescaleDB / SQLite / Redis)          │
│   Tables: fare_quotes | routes | index_daily | benchmarks   │
└──────────────┬───────────────────────────────┬──────────────┘
               │                               │
               ▼                               ▼
┌──────────────────────────────┐ ┌────────────────────────────┐
│         INDEX ENGINE         │ │       FASTAPI BACKEND      │
│   • Laspeyres Formula        │ │   /api/v1/index/daily      │
│   • DGCA Route Weights       │ │   /api/v1/fares/elasticity │
│   • Booking Window Horizon   │ │   /api/v1/export/nso       │
└──────────────────────────────┘ └─────────────┬──────────────┘
                                               │
                                               ▼
                                 ┌────────────────────────────┐
                                 │   REACT 18+ DASHBOARD      │
                                 │   • Live APIx Gauge        │
                                 │   • India Flight Map       │
                                 │   • Elasticity Curve       │
                                 │   • NSO CSV Exporter       │
                                 └────────────────────────────┘
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- Node.js 18+ and npm
- Docker & Docker Compose (Optional for containerized run)

### 2. Install Dependencies & Seed Database
```bash
# Clone the repository
git clone https://github.com/your-org/apix-prototype.git
cd apix-prototype

# Create Python virtual environment & install requirements
python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt

# Initialize database schema & seed historical 30-day baseline data
python db/seed_data.py
```

### 3. Start Backend Server
```bash
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```
- API Base: `http://localhost:8000`
- Interactive OpenAPI Docs: `http://localhost:8000/docs`

### 4. Start React Dashboard
```bash
cd frontend
npm install
npm run dev
```
- Dashboard URL: `http://localhost:5173` (or `http://localhost:3000`)

---

## 🧪 Running Tests
Run pytest with verbose output and coverage checks:
```bash
pytest tests/ -v
```

---

## 🐳 Docker Deployment
To launch the entire platform (TimescaleDB, Redis, Kafka, FastAPI, React Frontend) via Docker Compose:
```bash
docker-compose up -d --build
```

---

## 📊 DGCA Top 8 Domestic Route Basket
| Route | Origin → Dest | DGCA Weight ($w_r$) | DGCA Traffic Rank |
|---|---|---|---|
| DEL-BOM | Delhi ↔ Mumbai | **0.22** | 1 |
| DEL-BLR | Delhi ↔ Bengaluru | **0.18** | 2 |
| BOM-BLR | Mumbai ↔ Bengaluru | **0.14** | 3 |
| DEL-CCU | Delhi ↔ Kolkata | **0.12** | 4 |
| BLR-HYD | Bengaluru ↔ Hyderabad | **0.10** | 5 |
| MAA-DEL | Chennai ↔ Delhi | **0.09** | 6 |
| BOM-CCU | Mumbai ↔ Kolkata | **0.08** | 7 |
| DEL-MAA | Delhi ↔ Chennai | **0.07** | 8 |

---

## 📄 License & Ethical Compliance
Built for the Ministry of Statistics and Programme Implementation (MoSPI / NSO) under SIH 2026. See [LEGAL.md](file:///j:/CLG/Projects/SIH-2026/APIx-Prototype/LEGAL.md) for full compliance disclosures.
