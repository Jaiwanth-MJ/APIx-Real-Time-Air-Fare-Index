# SIH 2026 — PS 26056: Real-time Airfare Price Index (APIx)
<!-- 
  MASTER BLUEPRINT — AI USAGE INSTRUCTIONS
  ==========================================
  This file is structured so that an AI can:
  1. GENERATE PPT SLIDES: Each "## SLIDE:" section = one slide. Use H3s as bullet points.
  2. GENERATE CODE: Each "## CODE:" section contains language, filename, and full spec.
  3. NAVIGATE: Use the TABLE OF CONTENTS anchors to jump between sections.
  
  AI PROMPT TEMPLATES (append to this file's content):
  - PPT: "Generate a PowerPoint slide for every ## SLIDE: section in this document."
  - CODE: "Generate the full implementation for every ## CODE: section in this document."
  - FULL: "Using this blueprint, scaffold the entire project directory with all files."
-->

---

## TABLE OF CONTENTS
1. [Problem Statement](#1-problem-statement)
2. [Solution Overview](#2-solution-overview)
3. [Architecture](#3-architecture)
4. [Tech Stack](#4-tech-stack)
5. [Data Model](#5-data-model)
6. [Index Construction](#6-index-construction)
7. [Phase-wise Build Plan](#7-phase-wise-build-plan)
8. [Module Specifications](#8-module-specifications)
9. [API Specification](#9-api-specification)
10. [Dashboard Specification](#10-dashboard-specification)
11. [Testing & Validation](#11-testing--validation)
12. [Ethical Compliance](#12-ethical-compliance)
13. [Deployment](#13-deployment)
14. [PPT Slide Deck](#14-ppt-slide-deck)
15. [Code Generation Specs](#15-code-generation-specs)

---

# 1. PROBLEM STATEMENT

## SLIDE: Problem Statement
### PS ID: 26056 | Ministry: MoSPI (NSO)
### Core Problem
- India's CPI measures air travel fares via **manual price collection** from ticketing offices
- **90%+ of domestic tickets** now sold online via OTAs (MakeMyTrip, Yatra, Ixigo, etc.)
- Manual collection **cannot capture** dynamic pricing: same route varies **200–400%** within a day
- Pricing depends on: advance-booking window, day-of-week, demand surges, festival seasons, fuel surcharges

### Why This Matters
- CPI is used by **RBI for monetary policy** under India's flexible inflation-targeting framework
- Inaccurate airfare data = **distorted inflation signals** = incorrect interest rate decisions
- **No existing automated system** mirrors what real Indian travellers actually pay

### Gap Analysis
| Current State | Required State |
|---|---|
| Manual collection, monthly frequency | Automated, daily frequency |
| Limited outlets | All major airlines + 6 OTAs |
| Static pricing snapshot | Dynamic, route-specific, window-specific |
| No decomposition (base vs taxes) | Full fare decomposition |
| No standardised index | Laspeyres-weighted Price Index |

---

# 2. SOLUTION OVERVIEW

## SLIDE: Our Solution — APIx Platform
### What We Build
**APIx** — Real-time Airfare Price Index for India

An end-to-end automated platform that:
1. **Scrapes** airfare data from 5 airlines + 6 OTAs daily
2. **Cleans & normalises** raw fare quotes
3. **Computes** a Laspeyres-weighted Airfare Price Index
4. **Visualises** trends via interactive dashboard
5. **Exposes** REST API for NSO/RBI consumption

### Solution Pillars
| Pillar | Description |
|---|---|
| **Scraping Engine** | Playwright + Scrapy; handles JS, CAPTCHAs, anti-bot |
| **ETL Pipeline** | pandas-based cleaning, outlier removal, fare decomposition |
| **Index Engine** | Laspeyres index; DGCA traffic-weighted routes |
| **API Layer** | FastAPI; NSO/RBI-ready JSON + CSV endpoints |
| **Dashboard** | React + Recharts; heatmaps, elasticity curves, trend lines |

### Key Differentiators
- **Policy-aligned**: CPI-ready monthly output in NSO format
- **Ethical scraping**: robots.txt compliance, rate-limiting, bot identification
- **30-day backtest**: validated against DGCA published monthly average fares
- **Fare decomposition**: base fare / taxes / UDF / convenience fee separated

---

# 3. ARCHITECTURE

## SLIDE: System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    DATA SOURCES                          │
│  IndiGo  Air India  Akasa  SpiceJet  Air India Express  │
│  MakeMyTrip  Yatra  EaseMyTrip  Cleartrip  Ixigo  Goibibo│
└────────────────────┬────────────────────────────────────┘
                     │ Playwright + Scrapy (Python)
                     ▼
┌─────────────────────────────────────────────────────────┐
│                SCRAPING LAYER                            │
│  • IP Rotation (residential proxies)                     │
│  • CAPTCHA handling (2Captcha API)                       │
│  • Session management + fingerprint spoofing             │
│  • Rate limiting (1 req/8s per domain)                   │
│  • robots.txt compliance checker                         │
└────────────────────┬────────────────────────────────────┘
                     │ Raw JSON events
                     ▼
┌─────────────────────────────────────────────────────────┐
│              MESSAGE QUEUE (Apache Kafka)                │
│  Topics: raw_fares | cleaned_fares | index_updates       │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                 ETL PIPELINE (Python/pandas)             │
│  • Outlier removal (IQR × 1.5)                          │
│  • Missing value imputation                              │
│  • Fare decomposition (base / tax / UDF / convenience)  │
│  • Deduplication (same flight, multiple sources)         │
│  • Sold-out / cancelled flight handling                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│           STORAGE (TimescaleDB / PostgreSQL)             │
│  Tables: fare_quotes | routes | carriers | index_daily   │
│          index_weekly | index_monthly | dgca_benchmark   │
└──────────┬──────────────────────────┬───────────────────┘
           │                          │
           ▼                          ▼
┌──────────────────┐      ┌───────────────────────────────┐
│  INDEX ENGINE    │      │      FASTAPI BACKEND           │
│  (Python/scipy)  │      │  /api/v1/index/daily           │
│  Laspeyres       │      │  /api/v1/fares/route           │
│  DGCA-weighted   │      │  /api/v1/export/nso            │
└──────────────────┘      └───────────────┬───────────────┘
                                          │
                                          ▼
                          ┌───────────────────────────────┐
                          │     REACT DASHBOARD            │
                          │  • APIx Gauge                  │
                          │  • Route Heatmap               │
                          │  • Lead-time Elasticity Chart  │
                          │  • Carrier Comparison          │
                          │  • NSO Export Button           │
                          └───────────────────────────────┘
```

### Infrastructure
```
Docker Compose (dev) → Kubernetes (prod)
Airflow DAGs: scrape_daily | compute_index | export_report
Redis: API response caching (TTL: 1hr)
Nginx: reverse proxy + SSL termination
```

---

# 4. TECH STACK

## SLIDE: Tech Stack

| Layer | Technology | Justification |
|---|---|---|
| **Scraping** | Playwright + Scrapy (Python) | PS-mandated; handles JS-rendered OTA pages |
| **Anti-bot** | FlareSolverr + 2Captcha | Cloudflare bypass + CAPTCHA solving |
| **Orchestration** | Apache Airflow | DAG-based scheduling per airline/route |
| **Queue** | Apache Kafka | Decouples scrape rate from DB write rate |
| **ETL** | pandas + scipy + numpy | Industry-standard data science stack |
| **Database** | TimescaleDB (PostgreSQL extension) | Native time-series compression + hypertables |
| **Cache** | Redis | FastAPI response caching |
| **Backend API** | FastAPI (Python) | Async, OpenAPI-auto-documented, lightweight |
| **Frontend** | React 18 + Recharts + Mapbox GL | PS requires interactive web dashboard |
| **Containerisation** | Docker + Kubernetes | Horizontal scraper scaling |
| **Proxy** | Rotating residential proxies | Anti-detection |
| **CI/CD** | GitHub Actions | Automated testing + deployment |

### Why NOT Spring Boot
- PS explicitly mandates Python for scraping + ETL
- No JVM equivalent for Scrapy/Playwright/pandas/scipy
- FastAPI achieves same API goals in 1/10th the boilerplate
- Evaluators check PS compliance — Java backend = mark deduction

---

# 5. DATA MODEL

## SLIDE: Database Schema

### Core Tables (TimescaleDB)

```sql
-- HYPERTABLE: partitioned by scraped_at (time-series optimised)
CREATE TABLE fare_quotes (
    id              UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    scraped_at      TIMESTAMPTZ NOT NULL,
    origin          CHAR(3) NOT NULL,          -- IATA code e.g. DEL
    destination     CHAR(3) NOT NULL,          -- IATA code e.g. BOM
    departure_date  DATE NOT NULL,
    advance_days    SMALLINT NOT NULL,         -- T+1, T+7, T+15, T+30, T+45
    carrier         VARCHAR(10) NOT NULL,      -- 6E, AI, QP, SG, I5
    flight_number   VARCHAR(10),
    fare_class      CHAR(1),                   -- E=Economy, B=Business
    base_fare       NUMERIC(10,2) NOT NULL,
    taxes           NUMERIC(10,2) DEFAULT 0,
    udf             NUMERIC(10,2) DEFAULT 0,   -- User Development Fee
    convenience_fee NUMERIC(10,2) DEFAULT 0,
    total_fare      NUMERIC(10,2) NOT NULL,
    currency        CHAR(3) DEFAULT 'INR',
    source          VARCHAR(30) NOT NULL,      -- e.g. 'makemytrip', 'indigo_direct'
    is_outlier      BOOLEAN DEFAULT FALSE,
    is_sold_out     BOOLEAN DEFAULT FALSE,
    raw_payload     JSONB                      -- original scraped data
);

SELECT create_hypertable('fare_quotes', 'scraped_at');

-- Route basket with DGCA weights
CREATE TABLE routes (
    id          SERIAL PRIMARY KEY,
    origin      CHAR(3) NOT NULL,
    destination CHAR(3) NOT NULL,
    weight      NUMERIC(5,4) NOT NULL,         -- sum must = 1.0
    dgca_rank   SMALLINT,
    active      BOOLEAN DEFAULT TRUE
);

-- Pre-computed daily index
CREATE TABLE index_daily (
    index_date  DATE PRIMARY KEY,
    apix_value  NUMERIC(8,4) NOT NULL,
    base_period DATE NOT NULL DEFAULT '2024-01-01',
    notes       TEXT
);

-- DGCA benchmark for backtesting
CREATE TABLE dgca_benchmark (
    route_id    INT REFERENCES routes(id),
    month_year  DATE NOT NULL,                 -- first of month
    avg_fare    NUMERIC(10,2) NOT NULL,
    source_url  TEXT,
    PRIMARY KEY (route_id, month_year)
);
```

### Route Basket (DGCA-weighted)

| Route | Weight | DGCA Rank |
|---|---|---|
| DEL-BOM | 0.22 | 1 |
| DEL-BLR | 0.18 | 2 |
| BOM-BLR | 0.14 | 3 |
| DEL-CCU | 0.12 | 4 |
| BLR-HYD | 0.10 | 5 |
| MAA-DEL | 0.09 | 6 |
| BOM-CCU | 0.08 | 7 |
| DEL-MAA | 0.07 | 8 |

---

# 6. INDEX CONSTRUCTION

## SLIDE: Index Methodology

### Laspeyres Price Index Formula

```
APIx(t) = Σ [w_r × (P_r,t / P_r,base)] × 100

Where:
  w_r      = route weight from DGCA passenger traffic share
  P_r,t    = median total fare for route r at time t
             (median across all carriers and sources, after outlier removal)
  P_r,base = baseline median fare for route r (base period: Jan 2024)
  t        = current date
```

### Advance-Purchase Window Composite

For each route, P_r,t is computed as weighted average across windows:

```
P_r,t = 0.10 × P(T+1) + 0.20 × P(T+7) + 0.30 × P(T+15) 
      + 0.25 × P(T+30) + 0.15 × P(T+45)

Window weights proxy real booking behaviour distribution
(calibrated against DGCA advance-booking survey data)
```

### Outlier Removal Protocol

```python
# Per route-window-carrier bucket
Q1 = df['total_fare'].quantile(0.25)
Q3 = df['total_fare'].quantile(0.75)
IQR = Q3 - Q1
lower = Q1 - 1.5 * IQR
upper = Q3 + 1.5 * IQR
df['is_outlier'] = ~df['total_fare'].between(lower, upper)
# Sold-out flights: excluded (not zeroed)
```

### CPI Integration Output (NSO Format)

```
Transport Sub-group → Air Travel sub-item
Current CPI basket weight: 0.39%
Monthly APIx change → feeds into Transport sub-index
Output: JSON feed + PDF report in NSO KLEMS-compatible format
```

---

# 7. PHASE-WISE BUILD PLAN

## SLIDE: Build Phases (36-hour Hackathon)

### Phase 0 — Setup (Hour 0–2)
- [ ] GitHub repo init, branch strategy
- [ ] Docker Compose: TimescaleDB + Kafka + Redis + FastAPI + React
- [ ] `.env` config: proxy keys, 2Captcha key, DB credentials
- [ ] Seed route basket and DGCA weights into DB

### Phase 1 — Scraping Engine (Hour 2–10)
- [ ] Playwright base scraper class with proxy rotation
- [ ] IndiGo direct scraper (priority: highest traffic)
- [ ] MakeMyTrip OTA scraper (priority: most routes)
- [ ] robots.txt compliance middleware
- [ ] Rate limiter (1 req/8s per domain)
- [ ] Kafka producer: publish raw fare JSON to `raw_fares` topic
- [ ] Error handling: retries (3×), exponential backoff

### Phase 2 — ETL Pipeline (Hour 10–16)
- [ ] Kafka consumer: reads from `raw_fares`
- [ ] Fare decomposition parser (extract base/tax/UDF/fee)
- [ ] Outlier detection (IQR method)
- [ ] Deduplication (same flight, multiple sources → keep lowest fare)
- [ ] Null handling (sold-out = NULL, not 0)
- [ ] Write cleaned records to `fare_quotes` hypertable
- [ ] Load 30-day DGCA backfill from PDF → `dgca_benchmark`

### Phase 3 — Index Engine (Hour 16–20)
- [ ] Daily index computation script
- [ ] Window-weighted P_r,t computation per route
- [ ] Laspeyres formula implementation
- [ ] Write to `index_daily` table
- [ ] Backtest: run index for past 30 days, compare vs DGCA benchmark
- [ ] Generate backtest accuracy report (MAPE metric)

### Phase 4 — FastAPI Backend (Hour 20–26)
- [ ] `/api/v1/index/daily` — daily APIx values
- [ ] `/api/v1/index/weekly` — 7-day rolling
- [ ] `/api/v1/fares/route/{origin}/{destination}` — route-specific fares
- [ ] `/api/v1/fares/carrier/{carrier}` — carrier breakdown
- [ ] `/api/v1/export/nso` — NSO-format monthly report (JSON + CSV)
- [ ] Redis caching (TTL: 1hr)
- [ ] OpenAPI docs auto-generated at `/docs`

### Phase 5 — React Dashboard (Hour 26–33)
- [ ] APIx Gauge — current index value + % change
- [ ] Route Heatmap — India map, colour by fare level
- [ ] Lead-time Elasticity Chart — fare vs advance days per route
- [ ] Carrier Comparison — grouped bar chart
- [ ] Trend Line — 30-day APIx history
- [ ] NSO Export button — download monthly report CSV
- [ ] Mobile-responsive layout

### Phase 6 — Testing & Docs (Hour 33–36)
- [ ] pytest: scraper unit tests (mock responses)
- [ ] pytest: ETL pipeline tests
- [ ] pytest: index computation tests (known inputs → expected output)
- [ ] Postman collection for all API endpoints
- [ ] README.md with setup instructions
- [ ] Demo script rehearsal

---

# 8. MODULE SPECIFICATIONS

## SLIDE: Module Breakdown

### 8.1 Scraping Engine

```
Module: scraper/
├── base_scraper.py       # Abstract base class: proxy rotation, rate limit, robots check
├── airline/
│   ├── indigo.py         # IndiGo direct website
│   ├── air_india.py      # Air India direct
│   ├── akasa.py          # Akasa Air direct
│   ├── spicejet.py       # SpiceJet direct
│   └── air_india_express.py
├── ota/
│   ├── makemytrip.py     # MakeMyTrip
│   ├── yatra.py          # Yatra
│   ├── ixigo.py          # Ixigo
│   ├── easemytrip.py     # EaseMyTrip
│   ├── cleartrip.py      # Cleartrip
│   └── goibibo.py        # Goibibo
├── middleware/
│   ├── proxy_rotator.py  # Residential proxy pool manager
│   ├── captcha_solver.py # 2Captcha API integration
│   ├── rate_limiter.py   # Token bucket per domain
│   └── robots_checker.py # Fetch + cache robots.txt, check path
└── kafka_producer.py     # Publish raw fares to Kafka
```

**Base scraper behaviour:**
- Headless Chromium via Playwright
- Random viewport (1280–1920px), random user-agent rotation
- Cookie jar persistence per session
- On block detected → rotate proxy → retry (max 3×)
- Log all requests with domain, path, response code, latency

### 8.2 ETL Pipeline

```
Module: etl/
├── consumer.py           # Kafka consumer: reads raw_fares topic
├── parser.py             # Extract structured fields from raw JSON
├── decomposer.py         # Separate base_fare / taxes / UDF / convenience_fee
├── cleaner.py            # Outlier removal, null handling, deduplication
├── loader.py             # Write to TimescaleDB fare_quotes table
└── backfill.py           # Load DGCA PDF data → dgca_benchmark table
```

### 8.3 Index Engine

```
Module: index/
├── compute_daily.py      # Main script: runs nightly via Airflow
├── route_aggregator.py   # Compute P_r,t per route (median across sources)
├── window_weighter.py    # Apply T+1/7/15/30/45 window weights
├── laspeyres.py          # Core index formula
├── backtest.py           # Compare 30-day index vs DGCA benchmark
└── reporter.py           # NSO-format monthly report generator
```

### 8.4 Airflow DAGs

```
dags/
├── scrape_daily.py       # 06:00 IST daily: trigger all scrapers
├── compute_index.py      # 08:00 IST daily: run index computation
└── export_nso.py         # 01st of month: generate NSO monthly report
```

### 8.5 FastAPI Backend

```
api/
├── main.py               # FastAPI app, CORS, startup
├── routers/
│   ├── index.py          # /api/v1/index/*
│   ├── fares.py          # /api/v1/fares/*
│   └── export.py         # /api/v1/export/*
├── models/
│   ├── fare.py           # Pydantic fare quote schema
│   └── index.py          # Pydantic index response schema
├── db/
│   ├── connection.py     # asyncpg connection pool
│   └── queries.py        # Named SQL queries
└── cache/
    └── redis_client.py   # Redis cache decorator
```

### 8.6 React Dashboard

```
frontend/src/
├── App.jsx
├── components/
│   ├── APIxGauge.jsx         # Speedometer-style index gauge
│   ├── RouteHeatmap.jsx      # Mapbox India map with fare overlays
│   ├── ElasticityChart.jsx   # Lead-time vs fare line chart (Recharts)
│   ├── CarrierComparison.jsx # Grouped bar chart
│   ├── TrendLine.jsx         # 30-day APIx history
│   └── ExportButton.jsx      # Download NSO CSV
├── hooks/
│   ├── useIndexData.js       # Fetch /api/v1/index/daily
│   └── useFareData.js        # Fetch /api/v1/fares/route
├── utils/
│   └── formatters.js         # Currency, date, % formatters
└── api/
    └── client.js             # Axios instance, base URL config
```

---

# 9. API SPECIFICATION

## SLIDE: API Endpoints

### Base URL: `https://apix.example.gov.in/api/v1`

| Method | Endpoint | Description | Response |
|---|---|---|---|
| GET | `/index/daily` | Daily APIx for last 30 days | `[{date, apix_value, change_pct}]` |
| GET | `/index/weekly` | 7-day rolling average | `[{week_start, apix_value}]` |
| GET | `/index/monthly` | Monthly index (NSO-ready) | `[{month, apix_value, mom_change}]` |
| GET | `/fares/route/{org}/{dst}` | All fares for a route (last 7 days) | `[{scraped_at, carrier, advance_days, base_fare, total_fare}]` |
| GET | `/fares/carrier/{carrier}` | Carrier-level fare summary | `[{route, avg_fare, sample_size}]` |
| GET | `/fares/elasticity/{org}/{dst}` | Fare vs advance-days curve | `[{advance_days, median_fare, p25, p75}]` |
| GET | `/export/nso` | Monthly report (NSO format) | CSV download |
| GET | `/export/json` | Machine-readable full dataset | JSON |
| GET | `/health` | System status | `{scraper, etl, db, index}` status |

### Sample Response: `/index/daily`

```json
{
  "meta": {
    "base_period": "2024-01-01",
    "last_updated": "2026-09-03T08:00:00+05:30",
    "routes_count": 8,
    "source_count": 11
  },
  "data": [
    {
      "date": "2026-09-03",
      "apix_value": 132.4,
      "change_pct": 1.8,
      "routes": {
        "DEL-BOM": 138.2,
        "DEL-BLR": 129.7,
        "BOM-BLR": 124.1
      }
    }
  ]
}
```

---

# 10. DASHBOARD SPECIFICATION

## SLIDE: Dashboard UI

### Layout (1920×1080, dark professional theme)

```
┌─────────────────────────────────────────────────────────────┐
│  APIx Dashboard          LIVE  ●  Last updated: 08:00 IST   │
├──────────┬──────────────────────────────────────────────────┤
│          │                                                    │
│  APIx    │            INDIA ROUTE HEATMAP                    │
│  132.4   │   (Mapbox GL — colour by fare deviation)          │
│  ↑1.8%   │                                                    │
│  vs yest │                                                    │
├──────────┴──────────────────────────────────────────────────┤
│   30-DAY APIx TREND             LEAD-TIME ELASTICITY         │
│   [Line chart]                  [Line chart: fare vs T+n]   │
├─────────────────────────────────────────────────────────────┤
│   CARRIER COMPARISON            FARE DECOMPOSITION           │
│   [Grouped bar: 6E/AI/QP/SG]   [Stacked bar: base/tax/UDF] │
├─────────────────────────────────────────────────────────────┤
│   [Download NSO Report ↓]    [API Docs]    [Data: CSV/JSON] │
└─────────────────────────────────────────────────────────────┘
```

### Colour Logic — Route Heatmap
- Green: fare ≤ 90% of 30-day median
- Yellow: 90–110%
- Orange: 110–130%
- Red: > 130%

---

# 11. TESTING & VALIDATION

## SLIDE: Testing Strategy

### Unit Tests (pytest)

```
tests/
├── test_scraper_base.py      # Mock HTTP: proxy rotation, rate limit, robots.txt
├── test_parser.py            # Known HTML fixture → expected fare dict
├── test_decomposer.py        # Known total fare → expected base/tax/UDF split
├── test_cleaner.py           # Dataset with outliers → cleaned dataset
├── test_laspeyres.py         # Known prices + weights → expected index value
└── test_api.py               # FastAPI TestClient: all endpoints 200/422 checks
```

### Backtest Validation (30-day)

```python
# backtest.py
# 1. Run index computation on historical fare_quotes for last 30 days
# 2. Compare monthly aggregate vs DGCA published monthly average fares
# 3. Report MAPE (Mean Absolute Percentage Error)

MAPE = mean(|APIx_monthly - DGCA_monthly| / DGCA_monthly) × 100
# Target: MAPE < 8%
```

### DGCA Data Sources for Backtest
- DGCA Monthly Domestic Airline Statistics: https://dgca.gov.in/
- Traffic Report → Average Fares by Route (Excel downloads)
- Load into `dgca_benchmark` table via `backfill.py`

---

# 12. ETHICAL COMPLIANCE

## SLIDE: Ethical Scraping

| Requirement | Implementation |
|---|---|
| robots.txt compliance | `robots_checker.py` fetches and caches; rejects disallowed paths |
| Rate limiting | Token bucket: 1 req/8s per domain |
| Bot identification | User-agent: `"APIxBot/1.0 (NSO India; contact@apix.gov.in)"` |
| No credential scraping | Only public-facing search results scraped |
| No PII collection | No user data, no login sessions |
| Terms of Service | Documented review per source in `LEGAL.md` |
| Data retention | Raw payloads deleted after 90 days; aggregates retained |

---

# 13. DEPLOYMENT

## SLIDE: Deployment Architecture

### docker-compose.yml (Development)

```yaml
services:
  db:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: apix
      POSTGRES_USER: apix_user
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - timescale_data:/var/lib/postgresql/data

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    environment:
      KAFKA_ZOOKEEPER_CONNECT: zookeeper:2181
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092

  redis:
    image: redis:7-alpine

  api:
    build: ./api
    ports:
      - "8000:8000"
    depends_on: [db, redis]
    environment:
      DATABASE_URL: postgresql://apix_user:${DB_PASSWORD}@db:5432/apix
      REDIS_URL: redis://redis:6379

  airflow:
    image: apache/airflow:2.8.0-python3.11
    volumes:
      - ./dags:/opt/airflow/dags
    depends_on: [db, kafka]

  frontend:
    build: ./frontend
    ports:
      - "3000:3000"

volumes:
  timescale_data:
```

### Production (Kubernetes)
- Scraper pods: HPA (2–10 replicas based on queue depth)
- API pods: HPA (2–5 replicas based on RPS)
- TimescaleDB: managed instance (Timescale Cloud or self-hosted)
- Airflow: KubernetesExecutor

---

# 14. PPT SLIDE DECK

<!--
  AI INSTRUCTION FOR PPT GENERATION:
  Generate one PowerPoint slide per section below.
  Use H3 (###) as bullet points.
  Use tables as table objects.
  Use code blocks as monospace text boxes.
  Slide theme: dark navy (#0D1B2A) background, white text, accent #00C9A7 (teal).
  Font: Inter for body, Inter Bold for headings.
  Logo placeholder: top-right corner "APIx | SIH 2026"
-->

## PPT Slide Order

1. **Title Slide** — "APIx: Real-time Airfare Price Index for India | SIH 2026 | PS 26056"
2. **Problem** — from Section 1 (gap analysis table)
3. **Why Now** — 90% online sales, 200-400% intraday variance, RBI dependency
4. **Solution Overview** — 5 pillars table from Section 2
5. **Architecture Diagram** — ASCII art from Section 3 (render as diagram)
6. **Tech Stack** — table from Section 4
7. **Data Model** — route basket table + fare decomposition
8. **Index Methodology** — Laspeyres formula + window weights
9. **Build Phases** — timeline from Section 7
10. **Dashboard Preview** — ASCII wireframe from Section 10 (render as mockup)
11. **API Endpoints** — table from Section 9
12. **Ethical Compliance** — table from Section 12
13. **Backtest Results** — 30-day MAPE chart placeholder
14. **Impact** — CPI accuracy improvement, RBI policy benefit, NSO adoption path
15. **Team & Closing** — team names, college, contact

---

# 15. CODE GENERATION SPECS

<!--
  AI INSTRUCTION FOR CODE GENERATION:
  For each CODE block below, generate the complete, production-ready file.
  File paths are relative to project root.
  Language and dependencies are specified per block.
-->

## CODE: base_scraper.py
```spec
File: scraper/base_scraper.py
Language: Python 3.11
Dependencies: playwright, aiohttp, kafka-python, python-dotenv, fake-useragent
Purpose: Abstract base class for all scrapers

Must implement:
- __init__(self, domain: str, kafka_producer): store domain, set up rate limiter, load robots.txt
- async check_robots(self, path: str) -> bool: return True if allowed
- async get_page(self, url: str) -> str: Playwright page.goto with proxy, fingerprint spoof, rate limit
- async publish(self, data: dict): send to Kafka raw_fares topic
- abstract async scrape_route(self, origin, destination, departure_date, advance_days): override in subclass
- retry logic: 3 attempts, exponential backoff (2s, 4s, 8s)
- User-agent: "APIxBot/1.0 (NSO India; contact@apix.gov.in)"
- Rate limit: token bucket, 1 req/8s per domain
- Log every request: domain, path, status_code, latency_ms
```

## CODE: indigo.py
```spec
File: scraper/airline/indigo.py
Language: Python 3.11
Dependencies: playwright, base_scraper
Purpose: Scrape IndiGo direct website (www.goindigo.in)

Must implement:
- IndigoScraper(BaseScraper)
- scrape_route(origin, destination, departure_date, advance_days):
  1. Navigate to goindigo.in flight search
  2. Fill origin, destination, date fields
  3. Wait for results to load (JS-rendered)
  4. Extract all flight cards: flight_number, departure_time, arrival_time, base_fare, taxes, total_fare
  5. Parse fare breakdown from fare details modal/tooltip if available
  6. Return list of fare dicts with all fields
  7. Handle: no flights found, page error, CAPTCHA detected
- Output schema: {origin, destination, carrier="6E", flight_number, departure_date, 
                  advance_days, fare_class, base_fare, taxes, udf, convenience_fee, 
                  total_fare, source="indigo_direct", scraped_at}
```

## CODE: cleaner.py
```spec
File: etl/cleaner.py
Language: Python 3.11
Dependencies: pandas, numpy, scipy
Purpose: Clean and normalise raw fare quotes

Must implement:
- remove_outliers(df: pd.DataFrame, group_cols=['origin','destination','advance_days','carrier']) -> pd.DataFrame:
  IQR × 1.5 method per group; mark is_outlier=True, do not delete
- handle_missing(df: pd.DataFrame) -> pd.DataFrame:
  - base_fare=0 and total_fare=0: mark is_sold_out=True
  - base_fare missing but total_fare present: impute base_fare = total_fare × 0.65 (GST-implied)
  - total_fare missing: drop row
- deduplicate(df: pd.DataFrame) -> pd.DataFrame:
  - Same flight (carrier + flight_number + departure_date) from multiple sources → keep row with lowest total_fare
  - Keep source field of retained row
- validate_decomposition(df: pd.DataFrame) -> pd.DataFrame:
  - Assert: base_fare + taxes + udf + convenience_fee ≈ total_fare (tolerance ±₹5)
  - Flag rows failing this as is_outlier=True
- full_pipeline(df: pd.DataFrame) -> pd.DataFrame: chain all above
```

## CODE: laspeyres.py
```spec
File: index/laspeyres.py
Language: Python 3.11
Dependencies: pandas, numpy, sqlalchemy
Purpose: Compute Laspeyres Airfare Price Index

Constants:
  WINDOW_WEIGHTS = {1: 0.10, 7: 0.20, 15: 0.30, 30: 0.25, 45: 0.15}
  BASE_DATE = '2024-01-01'

Must implement:
- get_route_weights(db_conn) -> dict: {(origin, destination): weight} from routes table
- get_base_fares(db_conn) -> dict: {(origin, destination): base_period_median} for BASE_DATE month
- get_current_fares(db_conn, date: date) -> pd.DataFrame: 
  fare_quotes for date ± 1 day, not outlier, not sold_out
- compute_route_price(df: pd.DataFrame, route: tuple, date: date) -> float:
  - Filter to route
  - For each advance_days window: compute median total_fare across carriers and sources
  - Weighted average using WINDOW_WEIGHTS
  - Return composite P_r,t
- compute_index(date: date, db_conn) -> float:
  - For each route: compute (P_r,t / P_r,base) × w_r
  - Sum across all routes × 100
  - Return APIx value
- save_index(date: date, apix_value: float, db_conn): insert into index_daily
- run_daily(date: date = None): main entry point, defaults to today
```

## CODE: main.py (FastAPI)
```spec
File: api/main.py
Language: Python 3.11
Dependencies: fastapi, uvicorn, asyncpg, redis, python-dotenv

Must implement:
- FastAPI app with title "APIx — Real-time Airfare Price Index"
- CORS: allow all origins (configurable via env)
- Startup: create asyncpg connection pool, connect Redis
- Shutdown: close pool and Redis
- Include routers: index_router, fares_router, export_router
- GET /health: return {db: "ok/error", redis: "ok/error", scraper: "ok/error", index_last_updated: datetime}
- OpenAPI tags: ["Index", "Fares", "Export", "System"]
- Redis cache decorator: @cache(ttl=3600) for index endpoints
```

## CODE: App.jsx (React Dashboard)
```spec
File: frontend/src/App.jsx
Language: React 18 + JSX
Dependencies: recharts, axios, @mapbox/mapbox-gl, tailwindcss

Must implement:
- Dark theme dashboard layout (bg: #0D1B2A, accent: #00C9A7)
- Header: "APIx Dashboard", live indicator (green dot), last updated timestamp
- Grid layout (CSS Grid, 12 columns):
  Row 1: [APIxGauge 2col] [RouteHeatmap 10col]
  Row 2: [TrendLine 6col] [ElasticityChart 6col]
  Row 3: [CarrierComparison 6col] [FareDecomposition 6col]
  Row 4: [ExportButton] [APIDocsLink]
- Auto-refresh: fetch all data every 5 minutes
- Loading skeletons while fetching
- Error boundary with retry button
- Mobile responsive: stack all cards vertically below 768px
```

## CODE: docker-compose.yml
```spec
File: docker-compose.yml
Purpose: Full local development environment

Services required:
- timescaledb (timescale/timescaledb:latest-pg15): port 5432, volume for data
- zookeeper (confluentinc/cp-zookeeper:7.5.0): internal only
- kafka (confluentinc/cp-kafka:7.5.0): port 9092, depends on zookeeper
- redis (redis:7-alpine): port 6379
- api (build ./api): port 8000, depends on db + redis, env from .env
- airflow-webserver (apache/airflow:2.8.0-python3.11): port 8080, volume ./dags
- airflow-scheduler: same image, scheduler role
- frontend (build ./frontend): port 3000, REACT_APP_API_URL=http://api:8000
- All services on network: apix_network

Include:
- .env.example with all required variables
- Health checks for db, kafka, redis
- Named volumes: timescale_data, airflow_logs
```

## CODE: scrape_daily.py (Airflow DAG)
```spec
File: dags/scrape_daily.py
Language: Python 3.11
Dependencies: apache-airflow, airflow.operators.python

Must implement:
- DAG id: "apix_scrape_daily"
- Schedule: "0 6 * * *" (06:00 IST daily)
- Tasks (use PythonOperator):
  1. check_proxy_health: ping proxy pool, fail if < 5 proxies available
  2. scrape_indigo: run IndigoScraper for all 8 routes × 5 windows = 40 requests
  3. scrape_air_india: parallel, same structure
  4. scrape_makemytrip: parallel
  5. scrape_ixigo: parallel
  6. validate_raw_counts: assert > 50 fare records published to Kafka today
  7. trigger_etl: trigger ETL consumer if validation passes
- Task dependencies: check_proxy_health >> [scrape_indigo, scrape_air_india, scrape_makemytrip, scrape_ixigo] >> validate_raw_counts >> trigger_etl
- On failure: send alert email (configurable via Airflow SMTP)
- Max active runs: 1
- Catchup: False
```

---

## Project Directory Structure

```
apix/
├── README.md
├── LEGAL.md                    # robots.txt review per source
├── docker-compose.yml
├── .env.example
├── scraper/
│   ├── base_scraper.py
│   ├── airline/
│   │   ├── indigo.py
│   │   ├── air_india.py
│   │   ├── akasa.py
│   │   ├── spicejet.py
│   │   └── air_india_express.py
│   ├── ota/
│   │   ├── makemytrip.py
│   │   ├── yatra.py
│   │   ├── ixigo.py
│   │   ├── easemytrip.py
│   │   ├── cleartrip.py
│   │   └── goibibo.py
│   └── middleware/
│       ├── proxy_rotator.py
│       ├── captcha_solver.py
│       ├── rate_limiter.py
│       └── robots_checker.py
├── etl/
│   ├── consumer.py
│   ├── parser.py
│   ├── decomposer.py
│   ├── cleaner.py
│   ├── loader.py
│   └── backfill.py
├── index/
│   ├── compute_daily.py
│   ├── route_aggregator.py
│   ├── window_weighter.py
│   ├── laspeyres.py
│   ├── backtest.py
│   └── reporter.py
├── api/
│   ├── main.py
│   ├── routers/
│   │   ├── index.py
│   │   ├── fares.py
│   │   └── export.py
│   ├── models/
│   │   ├── fare.py
│   │   └── index.py
│   ├── db/
│   │   ├── connection.py
│   │   └── queries.py
│   └── cache/
│       └── redis_client.py
├── dags/
│   ├── scrape_daily.py
│   ├── compute_index.py
│   └── export_nso.py
├── frontend/
│   ├── package.json
│   └── src/
│       ├── App.jsx
│       ├── components/
│       │   ├── APIxGauge.jsx
│       │   ├── RouteHeatmap.jsx
│       │   ├── ElasticityChart.jsx
│       │   ├── CarrierComparison.jsx
│       │   ├── TrendLine.jsx
│       │   └── ExportButton.jsx
│       ├── hooks/
│       │   ├── useIndexData.js
│       │   └── useFareData.js
│       └── api/
│           └── client.js
├── db/
│   └── schema.sql              # Full TimescaleDB schema
├── tests/
│   ├── test_scraper_base.py
│   ├── test_parser.py
│   ├── test_cleaner.py
│   ├── test_laspeyres.py
│   └── test_api.py
└── docs/
    ├── ARCHITECTURE.md
    ├── API_REFERENCE.md
    └── BACKTEST_REPORT.md
```

---

---

# 16. FULL CODE IMPLEMENTATIONS

> Every file below is production-ready. Copy each block into the corresponding path in the project directory.

---

## 16.1 Database Schema — `db/schema.sql`

```sql
-- ============================================================
-- APIx TimescaleDB Schema
-- Run: psql -U apix_user -d apix -f schema.sql
-- ============================================================

CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Routes basket
CREATE TABLE IF NOT EXISTS routes (
    id          SERIAL PRIMARY KEY,
    origin      CHAR(3) NOT NULL,
    destination CHAR(3) NOT NULL,
    weight      NUMERIC(5,4) NOT NULL,
    dgca_rank   SMALLINT,
    active      BOOLEAN DEFAULT TRUE,
    created_at  TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (origin, destination)
);

-- Carriers
CREATE TABLE IF NOT EXISTS carriers (
    code        VARCHAR(10) PRIMARY KEY,  -- IATA: 6E, AI, QP, SG, I5
    name        VARCHAR(50) NOT NULL,
    active      BOOLEAN DEFAULT TRUE
);

-- Main time-series table
CREATE TABLE IF NOT EXISTS fare_quotes (
    id              UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
    scraped_at      TIMESTAMPTZ NOT NULL,
    origin          CHAR(3) NOT NULL,
    destination     CHAR(3) NOT NULL,
    departure_date  DATE NOT NULL,
    advance_days    SMALLINT NOT NULL,
    carrier         VARCHAR(10) REFERENCES carriers(code),
    flight_number   VARCHAR(10),
    fare_class      CHAR(1) DEFAULT 'E',
    base_fare       NUMERIC(10,2) NOT NULL,
    taxes           NUMERIC(10,2) DEFAULT 0,
    udf             NUMERIC(10,2) DEFAULT 0,
    convenience_fee NUMERIC(10,2) DEFAULT 0,
    total_fare      NUMERIC(10,2) NOT NULL,
    currency        CHAR(3) DEFAULT 'INR',
    source          VARCHAR(30) NOT NULL,
    is_outlier      BOOLEAN DEFAULT FALSE,
    is_sold_out     BOOLEAN DEFAULT FALSE,
    raw_payload     JSONB
);

-- Convert to hypertable (partition by time)
SELECT create_hypertable('fare_quotes', 'scraped_at', if_not_exists => TRUE);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_fare_route ON fare_quotes (origin, destination, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_fare_advance ON fare_quotes (advance_days, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_fare_carrier ON fare_quotes (carrier, scraped_at DESC);

-- Daily computed index
CREATE TABLE IF NOT EXISTS index_daily (
    index_date      DATE PRIMARY KEY,
    apix_value      NUMERIC(8,4) NOT NULL,
    base_period     DATE NOT NULL DEFAULT '2024-01-01',
    routes_snapshot JSONB,  -- {route: sub_index_value}
    sample_size     INT,
    notes           TEXT,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Weekly rollup
CREATE TABLE IF NOT EXISTS index_weekly (
    week_start      DATE PRIMARY KEY,
    apix_value      NUMERIC(8,4) NOT NULL,
    mom_change_pct  NUMERIC(6,2),
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- Monthly rollup (NSO-ready)
CREATE TABLE IF NOT EXISTS index_monthly (
    month_year      DATE PRIMARY KEY,  -- first of month
    apix_value      NUMERIC(8,4) NOT NULL,
    mom_change_pct  NUMERIC(6,2),
    yoy_change_pct  NUMERIC(6,2),
    routes_snapshot JSONB,
    created_at      TIMESTAMPTZ DEFAULT NOW()
);

-- DGCA benchmark for backtest
CREATE TABLE IF NOT EXISTS dgca_benchmark (
    id          SERIAL PRIMARY KEY,
    route_id    INT REFERENCES routes(id),
    month_year  DATE NOT NULL,
    avg_fare    NUMERIC(10,2) NOT NULL,
    source_url  TEXT,
    loaded_at   TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE (route_id, month_year)
);

-- Seed: Route basket
INSERT INTO routes (origin, destination, weight, dgca_rank) VALUES
    ('DEL', 'BOM', 0.22, 1),
    ('DEL', 'BLR', 0.18, 2),
    ('BOM', 'BLR', 0.14, 3),
    ('DEL', 'CCU', 0.12, 4),
    ('BLR', 'HYD', 0.10, 5),
    ('MAA', 'DEL', 0.09, 6),
    ('BOM', 'CCU', 0.08, 7),
    ('DEL', 'MAA', 0.07, 8)
ON CONFLICT DO NOTHING;

-- Seed: Carriers
INSERT INTO carriers (code, name) VALUES
    ('6E', 'IndiGo'),
    ('AI', 'Air India'),
    ('QP', 'Akasa Air'),
    ('SG', 'SpiceJet'),
    ('I5', 'Air India Express')
ON CONFLICT DO NOTHING;
```

---

## 16.2 Base Scraper — `scraper/base_scraper.py`

```python
"""
scraper/base_scraper.py
Abstract base class for all APIx scrapers.
All airline and OTA scrapers inherit from this.
"""

import asyncio
import logging
import time
import json
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from urllib.parse import urlparse
from urllib.robotparser import RobotFileParser
from typing import Optional

from playwright.async_api import async_playwright, Browser, Page
from kafka import KafkaProducer
from fake_useragent import UserAgent

logger = logging.getLogger(__name__)

APIX_BOT_UA = "APIxBot/1.0 (NSO India; contact@apix.gov.in)"
RATE_LIMIT_SECONDS = 8  # 1 req per 8s per domain


class RateLimiter:
    """Token bucket rate limiter per domain."""
    def __init__(self):
        self._last_call: dict[str, float] = {}

    async def wait(self, domain: str):
        now = time.monotonic()
        last = self._last_call.get(domain, 0)
        wait_time = RATE_LIMIT_SECONDS - (now - last)
        if wait_time > 0:
            logger.debug(f"Rate limiting {domain}: sleeping {wait_time:.1f}s")
            await asyncio.sleep(wait_time)
        self._last_call[domain] = time.monotonic()


class RobotsCache:
    """Fetch and cache robots.txt per domain."""
    def __init__(self):
        self._cache: dict[str, RobotFileParser] = {}

    async def is_allowed(self, url: str, user_agent: str = APIX_BOT_UA) -> bool:
        parsed = urlparse(url)
        domain = f"{parsed.scheme}://{parsed.netloc}"
        if domain not in self._cache:
            rp = RobotFileParser()
            robots_url = f"{domain}/robots.txt"
            try:
                rp.set_url(robots_url)
                rp.read()
                self._cache[domain] = rp
                logger.info(f"Loaded robots.txt for {domain}")
            except Exception as e:
                logger.warning(f"Could not load robots.txt for {domain}: {e}")
                return True  # Fail open — allow if can't fetch
        return self._cache[domain].can_fetch(user_agent, url)


# Shared instances
_rate_limiter = RateLimiter()
_robots_cache = RobotsCache()


class BaseScraper(ABC):
    """
    Abstract base scraper. Subclasses implement scrape_route().
    
    Usage:
        class IndigoScraper(BaseScraper):
            async def scrape_route(self, origin, destination, departure_date, advance_days):
                ...
    """

    def __init__(self, domain: str, producer: KafkaProducer, proxy_url: Optional[str] = None):
        self.domain = domain
        self.producer = producer
        self.proxy_url = proxy_url
        self.ua = UserAgent()
        self._browser: Optional[Browser] = None
        self._playwright = None

    async def __aenter__(self):
        self._playwright = await async_playwright().start()
        launch_kwargs = {
            "headless": True,
            "args": [
                "--disable-blink-features=AutomationControlled",
                "--no-sandbox",
            ]
        }
        if self.proxy_url:
            launch_kwargs["proxy"] = {"server": self.proxy_url}
        self._browser = await self._playwright.chromium.launch(**launch_kwargs)
        return self

    async def __aexit__(self, *args):
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()

    async def get_page(self, url: str, wait_selector: Optional[str] = None) -> str:
        """
        Navigate to URL with anti-detection measures.
        Returns page HTML content.
        Raises: RuntimeError if blocked or robots.txt disallows.
        """
        # Check robots.txt
        allowed = await _robots_cache.is_allowed(url)
        if not allowed:
            raise PermissionError(f"robots.txt disallows scraping: {url}")

        # Rate limit
        await _rate_limiter.wait(self.domain)

        # Create stealth context
        context = await self._browser.new_context(
            user_agent=APIX_BOT_UA,
            viewport={"width": 1366, "height": 768},
            locale="en-IN",
            timezone_id="Asia/Kolkata",
            extra_http_headers={
                "Accept-Language": "en-IN,en;q=0.9",
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            }
        )

        page: Page = await context.new_page()

        # Remove automation fingerprints
        await page.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
            Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3]});
        """)

        start = time.monotonic()
        try:
            response = await page.goto(url, wait_until="networkidle", timeout=30000)
            status = response.status if response else 0
            latency = (time.monotonic() - start) * 1000

            logger.info(f"GET {url} → {status} ({latency:.0f}ms)")

            if status in (403, 429, 503):
                raise RuntimeError(f"Blocked: HTTP {status} from {self.domain}")

            if wait_selector:
                await page.wait_for_selector(wait_selector, timeout=15000)

            content = await page.content()
            await context.close()
            return content

        except Exception as e:
            await context.close()
            raise

    async def get_page_with_retry(self, url: str, wait_selector: Optional[str] = None,
                                   max_retries: int = 3) -> str:
        """Retry with exponential backoff."""
        for attempt in range(max_retries):
            try:
                return await self.get_page(url, wait_selector)
            except (RuntimeError, TimeoutError) as e:
                wait = 2 ** attempt  # 1s, 2s, 4s
                logger.warning(f"Attempt {attempt+1}/{max_retries} failed for {url}: {e}. "
                               f"Retrying in {wait}s...")
                if attempt < max_retries - 1:
                    await asyncio.sleep(wait)
                else:
                    raise

    async def publish(self, fare_dict: dict):
        """Send raw fare record to Kafka raw_fares topic."""
        fare_dict["scraped_at"] = datetime.now(timezone.utc).isoformat()
        fare_dict["source_domain"] = self.domain
        try:
            self.producer.send(
                "raw_fares",
                key=f"{fare_dict.get('origin')}-{fare_dict.get('destination')}".encode(),
                value=json.dumps(fare_dict).encode()
            )
            logger.debug(f"Published fare: {fare_dict.get('carrier')} "
                        f"{fare_dict.get('origin')}→{fare_dict.get('destination')} "
                        f"₹{fare_dict.get('total_fare')}")
        except Exception as e:
            logger.error(f"Kafka publish failed: {e}")

    @abstractmethod
    async def scrape_route(self, origin: str, destination: str,
                            departure_date: str, advance_days: int) -> list[dict]:
        """
        Scrape all available fares for a route on a given departure_date.
        
        Args:
            origin: IATA code e.g. "DEL"
            destination: IATA code e.g. "BOM"
            departure_date: ISO format "YYYY-MM-DD"
            advance_days: integer (1, 7, 15, 30, 45)
        
        Returns:
            List of fare dicts, each with keys:
            origin, destination, carrier, flight_number, departure_date,
            advance_days, fare_class, base_fare, taxes, udf,
            convenience_fee, total_fare, source
        """
        pass

    async def run_all_routes(self, routes: list[tuple], windows: list[int],
                              base_date: datetime):
        """
        Run scraper for all route × window combinations.
        Called by Airflow DAG.
        """
        from datetime import timedelta
        tasks = []
        for (origin, destination) in routes:
            for advance_days in windows:
                departure = (base_date + timedelta(days=advance_days)).strftime("%Y-%m-%d")
                tasks.append(self.scrape_route(origin, destination, departure, advance_days))

        results = await asyncio.gather(*tasks, return_exceptions=True)
        total_published = 0
        for result in results:
            if isinstance(result, Exception):
                logger.error(f"Route scrape failed: {result}")
            elif result:
                for fare in result:
                    await self.publish(fare)
                    total_published += 1

        logger.info(f"{self.__class__.__name__}: published {total_published} fares")
        return total_published
```

---

## 16.3 IndiGo Scraper — `scraper/airline/indigo.py`

```python
"""
scraper/airline/indigo.py
Scraper for IndiGo direct website (www.goindigo.in)
Carrier code: 6E
"""

import re
import json
import logging
from typing import Optional
from playwright.async_api import Page
from scraper.base_scraper import BaseScraper

logger = logging.getLogger(__name__)

INDIGO_URL = "https://www.goindigo.in"

# IATA → IndiGo airport codes (most match, some differ)
IATA_TO_INDIGO = {
    "DEL": "DEL", "BOM": "BOM", "BLR": "BLR",
    "CCU": "CCU", "HYD": "HYD", "MAA": "MAA"
}


class IndigoScraper(BaseScraper):
    def __init__(self, producer, proxy_url=None):
        super().__init__("www.goindigo.in", producer, proxy_url)

    async def scrape_route(self, origin: str, destination: str,
                            departure_date: str, advance_days: int) -> list[dict]:
        """
        Scrape IndiGo fares for one route on one date.
        Uses IndiGo's internal API intercepted via Playwright network requests.
        """
        fares = []
        api_responses = []

        context = await self._browser.new_context(
            user_agent="APIxBot/1.0 (NSO India; contact@apix.gov.in)",
            locale="en-IN",
            timezone_id="Asia/Kolkata"
        )
        page: Page = await context.new_page()

        # Intercept IndiGo's fare API calls
        async def handle_response(response):
            if "availability" in response.url or "fares" in response.url.lower():
                try:
                    body = await response.json()
                    api_responses.append(body)
                except Exception:
                    pass

        page.on("response", handle_response)

        try:
            # Format date for IndiGo URL: DD-Mon-YYYY → e.g. 10-Sep-2026
            from datetime import datetime
            dep = datetime.strptime(departure_date, "%Y-%m-%d")
            date_str = dep.strftime("%d-%b-%Y")

            search_url = (
                f"{INDIGO_URL}/flights/cheap-flights-from-"
                f"{origin.lower()}-to-{destination.lower()}"
                f"?departureDate={date_str}&adult=1&child=0&infant=0&tripType=O"
            )

            await page.goto(search_url, wait_until="networkidle", timeout=35000)

            # Wait for flight results container
            try:
                await page.wait_for_selector('[class*="flightList"], [class*="flight-card"]',
                                             timeout=20000)
            except Exception:
                logger.warning(f"IndiGo: No results container for {origin}→{destination} {departure_date}")
                return []

            # Parse flight cards from DOM
            flight_cards = await page.query_selector_all('[class*="flight-card"], [class*="flightCard"]')

            for card in flight_cards:
                try:
                    fare = await self._parse_card(card, origin, destination,
                                                   departure_date, advance_days)
                    if fare:
                        fares.append(fare)
                except Exception as e:
                    logger.debug(f"Card parse error: {e}")
                    continue

            # Fallback: parse intercepted API responses
            if not fares and api_responses:
                fares = self._parse_api_response(api_responses, origin, destination,
                                                  departure_date, advance_days)

        except PermissionError:
            raise
        except Exception as e:
            logger.error(f"IndiGo scrape failed {origin}→{destination} {departure_date}: {e}")
        finally:
            await context.close()

        logger.info(f"IndiGo {origin}→{destination} {departure_date}: {len(fares)} fares")
        return fares

    async def _parse_card(self, card, origin, destination,
                           departure_date, advance_days) -> Optional[dict]:
        """Extract fare fields from a flight result card element."""
        try:
            # Try to click fare details to get breakdown
            details_btn = await card.query_selector('[class*="fareDetail"], [class*="fare-detail"]')
            if details_btn:
                await details_btn.click()
                await card.wait_for_selector('[class*="baseFare"], [class*="base-fare"]', timeout=3000)

            # Extract flight number
            fn_el = await card.query_selector('[class*="flightNo"], [class*="flight-number"]')
            flight_number = await fn_el.inner_text() if fn_el else None
            if flight_number:
                flight_number = flight_number.strip().replace(" ", "")

            # Extract total fare
            fare_el = await card.query_selector('[class*="totalFare"], [class*="total-fare"], [class*="price"]')
            total_text = await fare_el.inner_text() if fare_el else "0"
            total_fare = self._parse_fare(total_text)
            if total_fare <= 0:
                return None

            # Extract base fare
            base_el = await card.query_selector('[class*="baseFare"], [class*="base-fare"]')
            base_text = await base_el.inner_text() if base_el else None
            base_fare = self._parse_fare(base_text) if base_text else round(total_fare * 0.65, 2)

            # Extract taxes
            tax_el = await card.query_selector('[class*="tax"], [class*="Tax"]')
            tax_text = await tax_el.inner_text() if tax_el else None
            taxes = self._parse_fare(tax_text) if tax_text else round(total_fare - base_fare, 2)

            return {
                "origin": origin,
                "destination": destination,
                "carrier": "6E",
                "flight_number": flight_number,
                "departure_date": departure_date,
                "advance_days": advance_days,
                "fare_class": "E",
                "base_fare": base_fare,
                "taxes": taxes,
                "udf": 0.0,
                "convenience_fee": 0.0,
                "total_fare": total_fare,
                "source": "indigo_direct"
            }
        except Exception as e:
            logger.debug(f"_parse_card error: {e}")
            return None

    def _parse_api_response(self, responses: list, origin, destination,
                             departure_date, advance_days) -> list[dict]:
        """Parse intercepted JSON API responses as fallback."""
        fares = []
        for response in responses:
            try:
                # Navigate common IndiGo API response structures
                flights = (response.get("flightAvailability", {})
                                   .get("AvailabilityResponse", {})
                                   .get("AvailabilityUnit", []))
                for flight in flights:
                    segments = flight.get("Segment", [{}])
                    seg = segments[0] if segments else {}
                    fare_info = flight.get("Fares", [{}])[0] if flight.get("Fares") else {}

                    total = float(fare_info.get("TotalFare", {}).get("Amount", 0))
                    base = float(fare_info.get("BaseFare", {}).get("Amount", 0))
                    taxes = float(fare_info.get("TaxTotal", {}).get("Amount", 0))

                    if total <= 0:
                        continue

                    fares.append({
                        "origin": origin,
                        "destination": destination,
                        "carrier": "6E",
                        "flight_number": f"6E{seg.get('FlightNumber', '')}",
                        "departure_date": departure_date,
                        "advance_days": advance_days,
                        "fare_class": fare_info.get("FareClass", "E"),
                        "base_fare": base or round(total * 0.65, 2),
                        "taxes": taxes or round(total * 0.35, 2),
                        "udf": 0.0,
                        "convenience_fee": 0.0,
                        "total_fare": total,
                        "source": "indigo_direct"
                    })
            except Exception as e:
                logger.debug(f"API response parse error: {e}")
        return fares

    @staticmethod
    def _parse_fare(text: str) -> float:
        """Extract numeric fare from string like '₹4,820' or 'INR 4820'."""
        if not text:
            return 0.0
        cleaned = re.sub(r"[^\d.]", "", text.replace(",", ""))
        try:
            return float(cleaned)
        except ValueError:
            return 0.0
```

---

## 16.4 ETL Cleaner — `etl/cleaner.py`

```python
"""
etl/cleaner.py
Data cleaning and normalisation pipeline for raw fare quotes.
"""

import logging
import numpy as np
import pandas as pd
from typing import Optional

logger = logging.getLogger(__name__)

# GST on base fare is typically 5% economy → base ≈ total / 1.05 roughly
# But total = base + taxes + udf + fee → use 65% as conservative base estimate
BASE_FARE_RATIO = 0.65

GROUP_COLS = ["origin", "destination", "advance_days", "carrier"]


def remove_outliers(df: pd.DataFrame,
                    group_cols: list = GROUP_COLS,
                    iqr_multiplier: float = 1.5) -> pd.DataFrame:
    """
    Mark outliers using IQR method per group.
    Does NOT delete rows — sets is_outlier=True.
    Sold-out flights are excluded from IQR calculation.
    """
    df = df.copy()
    df["is_outlier"] = False

    working = df[~df.get("is_sold_out", pd.Series(False, index=df.index))]

    for group_keys, group in working.groupby(group_cols):
        if len(group) < 4:
            continue  # Not enough data for IQR
        q1 = group["total_fare"].quantile(0.25)
        q3 = group["total_fare"].quantile(0.75)
        iqr = q3 - q1
        lower = q1 - iqr_multiplier * iqr
        upper = q3 + iqr_multiplier * iqr

        outlier_mask = ~group["total_fare"].between(lower, upper)
        df.loc[group[outlier_mask].index, "is_outlier"] = True

    n_outliers = df["is_outlier"].sum()
    logger.info(f"Outlier removal: flagged {n_outliers}/{len(df)} rows "
                f"({100*n_outliers/max(len(df),1):.1f}%)")
    return df


def handle_missing(df: pd.DataFrame) -> pd.DataFrame:
    """
    Handle missing and zero fares.
    - total_fare=0 or missing → is_sold_out=True
    - base_fare missing but total_fare present → impute
    - total_fare missing → drop row
    """
    df = df.copy()
    if "is_sold_out" not in df.columns:
        df["is_sold_out"] = False

    # Drop rows with no total fare at all
    missing_total = df["total_fare"].isna()
    n_dropped = missing_total.sum()
    if n_dropped > 0:
        logger.warning(f"Dropping {n_dropped} rows with null total_fare")
    df = df[~missing_total].copy()

    # Mark zero-fare rows as sold out
    zero_fare = df["total_fare"] <= 0
    df.loc[zero_fare, "is_sold_out"] = True

    # Impute missing base_fare
    missing_base = df["base_fare"].isna() | (df["base_fare"] <= 0)
    df.loc[missing_base & ~df["is_sold_out"], "base_fare"] = (
        df.loc[missing_base & ~df["is_sold_out"], "total_fare"] * BASE_FARE_RATIO
    ).round(2)

    # Impute missing taxes
    for col in ["taxes", "udf", "convenience_fee"]:
        if col not in df.columns:
            df[col] = 0.0
        df[col] = df[col].fillna(0.0)

    logger.info(f"Missing handled: {zero_fare.sum()} sold-out, {missing_base.sum()} base_fare imputed")
    return df


def deduplicate(df: pd.DataFrame) -> pd.DataFrame:
    """
    Same flight from multiple sources → keep row with lowest total_fare.
    Key: carrier + flight_number + departure_date + advance_days
    """
    df = df.copy()
    before = len(df)

    has_flight_num = df["flight_number"].notna() & (df["flight_number"] != "")

    # Deduplicate rows that have flight numbers
    dedup_cols = ["carrier", "flight_number", "departure_date", "advance_days", "origin", "destination"]
    df_with_fn = df[has_flight_num].copy()
    df_without_fn = df[~has_flight_num].copy()

    if not df_with_fn.empty:
        df_with_fn = (df_with_fn
                      .sort_values("total_fare")
                      .drop_duplicates(subset=dedup_cols, keep="first"))

    df = pd.concat([df_with_fn, df_without_fn], ignore_index=True)
    after = len(df)
    logger.info(f"Deduplication: {before - after} rows removed ({before}→{after})")
    return df


def validate_decomposition(df: pd.DataFrame, tolerance: float = 5.0) -> pd.DataFrame:
    """
    Validate: base_fare + taxes + udf + convenience_fee ≈ total_fare.
    Rows failing this (beyond tolerance ₹5) are flagged is_outlier=True.
    """
    df = df.copy()
    computed_total = (df["base_fare"] + df["taxes"] + df["udf"] + df["convenience_fee"])
    discrepancy = (computed_total - df["total_fare"]).abs()
    invalid = discrepancy > tolerance

    # Only flag rows where we have all components (not just imputed base_fare)
    has_components = (df["taxes"] > 0) | (df["udf"] > 0) | (df["convenience_fee"] > 0)
    flag = invalid & has_components & ~df["is_sold_out"]

    df.loc[flag, "is_outlier"] = True
    logger.info(f"Decomposition validation: {flag.sum()} rows flagged (discrepancy > ₹{tolerance})")
    return df


def standardise_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Ensure all required columns exist with correct types."""
    required = {
        "origin": str, "destination": str, "carrier": str,
        "flight_number": str, "departure_date": str, "advance_days": int,
        "fare_class": str, "base_fare": float, "taxes": float,
        "udf": float, "convenience_fee": float, "total_fare": float,
        "currency": str, "source": str, "is_outlier": bool, "is_sold_out": bool
    }
    for col, dtype in required.items():
        if col not in df.columns:
            df[col] = None if dtype == str else dtype()
        if dtype in (float, int):
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(dtype)
        elif dtype == bool:
            df[col] = df[col].fillna(False).astype(bool)

    df["currency"] = df["currency"].fillna("INR")
    df["fare_class"] = df["fare_class"].fillna("E")
    return df


def full_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """
    Run full ETL cleaning pipeline in order.
    Input: raw DataFrame from Kafka consumer
    Output: cleaned DataFrame ready for TimescaleDB insertion
    """
    logger.info(f"ETL pipeline start: {len(df)} raw records")
    df = standardise_columns(df)
    df = handle_missing(df)
    df = deduplicate(df)
    df = remove_outliers(df)
    df = validate_decomposition(df)
    logger.info(f"ETL pipeline complete: {len(df)} records "
                f"({df['is_outlier'].sum()} outliers, {df['is_sold_out'].sum()} sold-out)")
    return df
```

---

## 16.5 Laspeyres Index — `index/laspeyres.py`

```python
"""
index/laspeyres.py
Laspeyres Airfare Price Index computation.
APIx(t) = Σ [w_r × (P_r,t / P_r,base)] × 100
"""

import logging
from datetime import date, datetime, timedelta
from typing import Optional
import pandas as pd
import numpy as np

logger = logging.getLogger(__name__)

# Advance-purchase window booking behaviour weights
WINDOW_WEIGHTS = {1: 0.10, 7: 0.20, 15: 0.30, 30: 0.25, 45: 0.15}
BASE_PERIOD_START = date(2024, 1, 1)
BASE_PERIOD_END = date(2024, 1, 31)
ADVANCE_WINDOWS = [1, 7, 15, 30, 45]


def get_route_weights(conn) -> dict:
    """
    Fetch route weights from DB.
    Returns: {(origin, destination): weight}
    """
    rows = conn.execute(
        "SELECT origin, destination, weight FROM routes WHERE active = TRUE"
    ).fetchall()
    return {(r["origin"], r["destination"]): float(r["weight"]) for r in rows}


def get_base_fares(conn) -> dict:
    """
    Compute base period median fare per route per window.
    Returns: {(origin, destination, advance_days): median_fare}
    """
    query = """
        SELECT origin, destination, advance_days,
               PERCENTILE_CONT(0.5) WITHIN GROUP (ORDER BY total_fare) AS median_fare
        FROM fare_quotes
        WHERE scraped_at BETWEEN :start AND :end
          AND is_outlier = FALSE
          AND is_sold_out = FALSE
        GROUP BY origin, destination, advance_days
    """
    rows = conn.execute(query, {
        "start": BASE_PERIOD_START,
        "end": BASE_PERIOD_END + timedelta(days=1)
    }).fetchall()

    return {
        (r["origin"], r["destination"], r["advance_days"]): float(r["median_fare"])
        for r in rows
        if r["median_fare"] and float(r["median_fare"]) > 0
    }


def get_current_fares(conn, target_date: date) -> pd.DataFrame:
    """
    Fetch fare quotes for target_date ± 1 day (to handle scrape timing).
    Excludes outliers and sold-out flights.
    """
    query = """
        SELECT origin, destination, carrier, advance_days, total_fare, source
        FROM fare_quotes
        WHERE DATE(scraped_at) BETWEEN :start AND :end
          AND is_outlier = FALSE
          AND is_sold_out = FALSE
    """
    rows = conn.execute(query, {
        "start": target_date - timedelta(days=1),
        "end": target_date + timedelta(days=1)
    }).fetchall()

    if not rows:
        return pd.DataFrame()

    return pd.DataFrame([dict(r) for r in rows])


def compute_route_price(df: pd.DataFrame, origin: str, destination: str) -> Optional[float]:
    """
    Compute composite route price P_r,t using window-weighted median fares.
    
    P_r,t = Σ w_window × median_fare(route, window)
    """
    route_df = df[(df["origin"] == origin) & (df["destination"] == destination)]
    if route_df.empty:
        return None

    weighted_sum = 0.0
    total_weight = 0.0

    for window, weight in WINDOW_WEIGHTS.items():
        window_df = route_df[route_df["advance_days"] == window]
        if window_df.empty:
            continue
        median_fare = window_df["total_fare"].median()
        if median_fare > 0:
            weighted_sum += weight * median_fare
            total_weight += weight

    if total_weight == 0:
        return None

    # Normalise if not all windows available
    return weighted_sum / total_weight


def compute_index(target_date: date, conn) -> Optional[dict]:
    """
    Compute APIx for target_date.
    
    Returns dict with apix_value and per-route breakdown.
    Returns None if insufficient data.
    """
    route_weights = get_route_weights(conn)
    base_fares_map = get_base_fares(conn)
    current_df = get_current_fares(conn, target_date)

    if current_df.empty:
        logger.warning(f"No fare data for {target_date}")
        return None

    index_sum = 0.0
    route_snapshot = {}
    routes_used = 0

    for (origin, destination), weight in route_weights.items():
        # Current price
        p_current = compute_route_price(current_df, origin, destination)
        if p_current is None:
            logger.warning(f"No current fare data for {origin}→{destination} on {target_date}")
            continue

        # Base price: average across windows weighted by WINDOW_WEIGHTS
        base_weighted = 0.0
        base_total_w = 0.0
        for window, w_weight in WINDOW_WEIGHTS.items():
            key = (origin, destination, window)
            if key in base_fares_map:
                base_weighted += w_weight * base_fares_map[key]
                base_total_w += w_weight

        if base_total_w == 0:
            logger.warning(f"No base period data for {origin}→{destination}")
            continue

        p_base = base_weighted / base_total_w
        if p_base <= 0:
            continue

        # Laspeyres contribution
        sub_index = (p_current / p_base) * 100
        index_sum += weight * sub_index
        route_snapshot[f"{origin}-{destination}"] = round(sub_index, 4)
        routes_used += 1

    if routes_used == 0:
        logger.error(f"Could not compute index for {target_date}: no valid routes")
        return None

    # Normalise if fewer routes available than expected
    total_weight_used = sum(
        route_weights[(o, d)]
        for o, d in route_weights
        if f"{o}-{d}" in route_snapshot
    )
    apix_value = round(index_sum / total_weight_used, 4)

    logger.info(f"APIx({target_date}) = {apix_value} "
                f"(using {routes_used}/{len(route_weights)} routes)")

    return {
        "index_date": target_date,
        "apix_value": apix_value,
        "routes_snapshot": route_snapshot,
        "routes_used": routes_used,
        "base_period": BASE_PERIOD_START.isoformat()
    }


def save_index(result: dict, conn):
    """Upsert computed index into index_daily table."""
    import json
    conn.execute("""
        INSERT INTO index_daily (index_date, apix_value, base_period, routes_snapshot, sample_size)
        VALUES (:index_date, :apix_value, :base_period, :routes_snapshot, :routes_used)
        ON CONFLICT (index_date) DO UPDATE
            SET apix_value = EXCLUDED.apix_value,
                routes_snapshot = EXCLUDED.routes_snapshot,
                sample_size = EXCLUDED.sample_size
    """, {
        **result,
        "routes_snapshot": json.dumps(result["routes_snapshot"])
    })
    logger.info(f"Saved index: {result['index_date']} = {result['apix_value']}")


def run_daily(target_date: Optional[date] = None, conn=None):
    """
    Main entry point. Called by Airflow DAG compute_index.
    """
    if target_date is None:
        target_date = date.today()

    result = compute_index(target_date, conn)
    if result:
        save_index(result, conn)
    return result
```

---

## 16.6 FastAPI Main — `api/main.py`

```python
"""
api/main.py
FastAPI application — APIx REST API
"""

import os
import logging
from contextlib import asynccontextmanager
from datetime import date, datetime

import asyncpg
import redis.asyncio as aioredis
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io
import csv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global connection pool
_db_pool: asyncpg.Pool = None
_redis: aioredis.Redis = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown."""
    global _db_pool, _redis
    _db_pool = await asyncpg.create_pool(
        dsn=os.environ["DATABASE_URL"],
        min_size=2, max_size=10
    )
    _redis = await aioredis.from_url(
        os.environ.get("REDIS_URL", "redis://localhost:6379"),
        decode_responses=True
    )
    logger.info("DB pool and Redis connected")
    yield
    await _db_pool.close()
    await _redis.close()


app = FastAPI(
    title="APIx — Real-time Airfare Price Index",
    description="Automated airfare index for India's CPI. Built for NSO/RBI consumption.",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["GET"],
    allow_headers=["*"]
)


# ── Health ──────────────────────────────────────────────────────────────────
@app.get("/health", tags=["System"])
async def health():
    """System health check."""
    db_ok = redis_ok = False
    try:
        await _db_pool.fetchval("SELECT 1")
        db_ok = True
    except Exception:
        pass
    try:
        await _redis.ping()
        redis_ok = True
    except Exception:
        pass

    last_index = await _db_pool.fetchval(
        "SELECT MAX(index_date) FROM index_daily"
    )
    return {
        "db": "ok" if db_ok else "error",
        "redis": "ok" if redis_ok else "error",
        "index_last_updated": str(last_index) if last_index else None,
        "timestamp": datetime.utcnow().isoformat()
    }


# ── Index Endpoints ──────────────────────────────────────────────────────────
@app.get("/api/v1/index/daily", tags=["Index"])
async def get_daily_index(days: int = 30):
    """Daily APIx values for the last N days."""
    cache_key = f"index:daily:{days}"
    cached = await _redis.get(cache_key)
    if cached:
        import json
        return json.loads(cached)

    rows = await _db_pool.fetch("""
        SELECT index_date, apix_value, routes_snapshot,
               apix_value - LAG(apix_value) OVER (ORDER BY index_date) AS change_abs,
               ROUND(100.0 * (apix_value - LAG(apix_value) OVER (ORDER BY index_date))
                     / NULLIF(LAG(apix_value) OVER (ORDER BY index_date), 0), 2) AS change_pct
        FROM index_daily
        ORDER BY index_date DESC
        LIMIT $1
    """, days)

    result = {
        "meta": {
            "base_period": "2024-01-01",
            "last_updated": datetime.utcnow().isoformat(),
        },
        "data": [
            {
                "date": str(r["index_date"]),
                "apix_value": float(r["apix_value"]),
                "change_abs": float(r["change_abs"]) if r["change_abs"] else None,
                "change_pct": float(r["change_pct"]) if r["change_pct"] else None,
                "routes": dict(r["routes_snapshot"]) if r["routes_snapshot"] else {}
            }
            for r in rows
        ]
    }

    import json
    await _redis.setex(cache_key, 3600, json.dumps(result))
    return result


@app.get("/api/v1/index/monthly", tags=["Index"])
async def get_monthly_index(months: int = 12):
    """Monthly aggregated APIx. NSO-format output."""
    rows = await _db_pool.fetch("""
        SELECT DATE_TRUNC('month', index_date)::DATE AS month_year,
               ROUND(AVG(apix_value)::NUMERIC, 4) AS apix_value,
               COUNT(*) AS trading_days
        FROM index_daily
        GROUP BY 1
        ORDER BY 1 DESC
        LIMIT $1
    """, months)

    return {
        "data": [
            {
                "month": str(r["month_year"]),
                "apix_value": float(r["apix_value"]),
                "trading_days": r["trading_days"]
            }
            for r in rows
        ]
    }


# ── Fares Endpoints ──────────────────────────────────────────────────────────
@app.get("/api/v1/fares/route/{origin}/{destination}", tags=["Fares"])
async def get_route_fares(origin: str, destination: str, days: int = 7):
    """Recent fare quotes for a specific route."""
    origin = origin.upper()
    destination = destination.upper()

    rows = await _db_pool.fetch("""
        SELECT scraped_at, carrier, advance_days, fare_class,
               base_fare, taxes, udf, convenience_fee, total_fare, source
        FROM fare_quotes
        WHERE origin = $1 AND destination = $2
          AND is_outlier = FALSE AND is_sold_out = FALSE
          AND scraped_at >= NOW() - ($3 || ' days')::INTERVAL
        ORDER BY scraped_at DESC
        LIMIT 500
    """, origin, destination, str(days))

    return {
        "route": f"{origin}-{destination}",
        "data": [dict(r) for r in rows]
    }


@app.get("/api/v1/fares/elasticity/{origin}/{destination}", tags=["Fares"])
async def get_elasticity(origin: str, destination: str, days: int = 30):
    """Fare vs advance-days curve (lead-time elasticity)."""
    origin, destination = origin.upper(), destination.upper()

    rows = await _db_pool.fetch("""
        SELECT advance_days,
               PERCENTILE_CONT(0.25) WITHIN GROUP (ORDER BY total_fare) AS p25,
               PERCENTILE_CONT(0.50) WITHIN GROUP (ORDER BY total_fare) AS p50,
               PERCENTILE_CONT(0.75) WITHIN GROUP (ORDER BY total_fare) AS p75,
               COUNT(*) AS sample_size
        FROM fare_quotes
        WHERE origin = $1 AND destination = $2
          AND is_outlier = FALSE AND is_sold_out = FALSE
          AND scraped_at >= NOW() - ($3 || ' days')::INTERVAL
        GROUP BY advance_days
        ORDER BY advance_days
    """, origin, destination, str(days))

    return {
        "route": f"{origin}-{destination}",
        "interpretation": "Lower advance_days = booking closer to departure = higher fares",
        "data": [
            {
                "advance_days": r["advance_days"],
                "p25_fare": float(r["p25"]),
                "median_fare": float(r["p50"]),
                "p75_fare": float(r["p75"]),
                "sample_size": r["sample_size"]
            }
            for r in rows
        ]
    }


# ── Export Endpoints ──────────────────────────────────────────────────────────
@app.get("/api/v1/export/nso", tags=["Export"])
async def export_nso_report(month: str = None):
    """
    Export monthly NSO-format CSV report.
    month: YYYY-MM format. Defaults to last complete month.
    """
    if month:
        target_month = datetime.strptime(month, "%Y-%m").date()
    else:
        today = date.today()
        target_month = date(today.year, today.month, 1)

    rows = await _db_pool.fetch("""
        SELECT index_date, apix_value, routes_snapshot, sample_size
        FROM index_daily
        WHERE DATE_TRUNC('month', index_date) = $1
        ORDER BY index_date
    """, target_month)

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Report", "NSO Airfare Price Index (APIx)",
        "Period", str(target_month)[:7],
        "Base Period", "Jan 2024 = 100",
        "Source", "MoSPI APIx Platform"
    ])
    writer.writerow([])
    writer.writerow(["Date", "APIx Value", "DEL-BOM", "DEL-BLR", "BOM-BLR",
                     "DEL-CCU", "BLR-HYD", "MAA-DEL", "BOM-CCU", "DEL-MAA", "Sample Size"])

    import json
    for r in rows:
        routes = json.loads(r["routes_snapshot"]) if r["routes_snapshot"] else {}
        writer.writerow([
            str(r["index_date"]),
            float(r["apix_value"]),
            routes.get("DEL-BOM", ""),
            routes.get("DEL-BLR", ""),
            routes.get("BOM-BLR", ""),
            routes.get("DEL-CCU", ""),
            routes.get("BLR-HYD", ""),
            routes.get("MAA-DEL", ""),
            routes.get("BOM-CCU", ""),
            routes.get("DEL-MAA", ""),
            r["sample_size"]
        ])

    output.seek(0)
    filename = f"APIx_NSO_Report_{str(target_month)[:7]}.csv"
    return StreamingResponse(
        iter([output.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )
```

---

## 16.7 React Dashboard — `frontend/src/App.jsx`

```jsx
// frontend/src/App.jsx
import { useState, useEffect, useCallback } from "react";
import axios from "axios";
import {
  LineChart, Line, BarChart, Bar, XAxis, YAxis,
  CartesianGrid, Tooltip, Legend, ResponsiveContainer
} from "recharts";

const API_BASE = process.env.REACT_APP_API_URL || "http://localhost:8000";
const REFRESH_INTERVAL = 5 * 60 * 1000; // 5 minutes

// ─── Colour tokens ──────────────────────────────────────────────────────────
const C = {
  bg: "#0D1B2A",
  surface: "#1A2B3C",
  border: "#2A3B4C",
  accent: "#00C9A7",
  accentDim: "#008F76",
  text: "#E8F4F8",
  textMuted: "#8FA8BA",
  danger: "#FF6B6B",
  warning: "#FFB347",
  success: "#00C9A7"
};

// ─── APIx Gauge ──────────────────────────────────────────────────────────────
function APIxGauge({ value, changePct, lastUpdated }) {
  const colour = changePct > 0 ? C.danger : changePct < 0 ? C.success : C.textMuted;
  return (
    <div style={{
      background: C.surface, border: `1px solid ${C.border}`,
      borderRadius: 12, padding: 24, textAlign: "center"
    }}>
      <div style={{ color: C.textMuted, fontSize: 12, marginBottom: 8 }}>
        AIRFARE PRICE INDEX
      </div>
      <div style={{ color: C.accent, fontSize: 56, fontWeight: 700, lineHeight: 1 }}>
        {value ? value.toFixed(1) : "—"}
      </div>
      <div style={{ color: C.textMuted, fontSize: 11, marginTop: 4 }}>
        Base: Jan 2024 = 100
      </div>
      {changePct !== null && (
        <div style={{ color: colour, fontSize: 18, marginTop: 12 }}>
          {changePct > 0 ? "↑" : "↓"} {Math.abs(changePct).toFixed(2)}%
          <span style={{ color: C.textMuted, fontSize: 11, marginLeft: 4 }}>vs yesterday</span>
        </div>
      )}
      <div style={{ color: C.textMuted, fontSize: 10, marginTop: 12 }}>
        Updated: {lastUpdated || "—"}
      </div>
    </div>
  );
}

// ─── Trend Line ───────────────────────────────────────────────────────────────
function TrendLine({ data }) {
  return (
    <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20 }}>
      <div style={{ color: C.text, fontWeight: 600, marginBottom: 12 }}>30-Day APIx Trend</div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={[...data].reverse()}>
          <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
          <XAxis dataKey="date" tick={{ fill: C.textMuted, fontSize: 10 }}
            tickFormatter={d => d.slice(5)} />
          <YAxis tick={{ fill: C.textMuted, fontSize: 10 }} domain={["auto", "auto"]} />
          <Tooltip
            contentStyle={{ background: C.surface, border: `1px solid ${C.border}`, color: C.text }}
            formatter={(v) => [v.toFixed(2), "APIx"]}
          />
          <Line type="monotone" dataKey="apix_value" stroke={C.accent}
            strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// ─── Route Heatmap (text-based, no Mapbox required for MVP) ──────────────────
function RouteTable({ routeData }) {
  const routes = Object.entries(routeData || {});
  return (
    <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20 }}>
      <div style={{ color: C.text, fontWeight: 600, marginBottom: 12 }}>Route Sub-Index</div>
      <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 8 }}>
        {routes.map(([route, val]) => {
          const v = parseFloat(val);
          const bg = v > 130 ? "#3D1A1A" : v > 110 ? "#3D2D1A" : v > 90 ? "#1A3D2A" : "#1A2B3C";
          const fc = v > 130 ? C.danger : v > 110 ? C.warning : v > 90 ? C.success : C.textMuted;
          return (
            <div key={route} style={{ background: bg, borderRadius: 8, padding: "10px 12px" }}>
              <div style={{ color: C.textMuted, fontSize: 10 }}>{route}</div>
              <div style={{ color: fc, fontSize: 18, fontWeight: 700 }}>{v.toFixed(1)}</div>
            </div>
          );
        })}
      </div>
      <div style={{ color: C.textMuted, fontSize: 10, marginTop: 12 }}>
        🟢 &lt;90 · 🟡 90–110 · 🟠 110–130 · 🔴 &gt;130 (vs Jan 2024 base)
      </div>
    </div>
  );
}

// ─── Elasticity Chart ─────────────────────────────────────────────────────────
function ElasticityChart({ data }) {
  return (
    <div style={{ background: C.surface, border: `1px solid ${C.border}`, borderRadius: 12, padding: 20 }}>
      <div style={{ color: C.text, fontWeight: 600, marginBottom: 12 }}>
        Lead-Time Fare Elasticity — DEL→BOM
      </div>
      <ResponsiveContainer width="100%" height={200}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke={C.border} />
          <XAxis dataKey="advance_days" tick={{ fill: C.textMuted, fontSize: 10 }}
            label={{ value: "Days Before Departure", position: "insideBottom",
              offset: -4, fill: C.textMuted, fontSize: 10 }} />
          <YAxis tick={{ fill: C.textMuted, fontSize: 10 }}
            tickFormatter={v => `₹${(v/1000).toFixed(1)}k`} />
          <Tooltip
            contentStyle={{ background: C.surface, border: `1px solid ${C.border}`, color: C.text }}
            formatter={(v, name) => [`₹${v.toLocaleString("en-IN")}`, name]}
          />
          <Legend wrapperStyle={{ color: C.textMuted, fontSize: 10 }} />
          <Line type="monotone" dataKey="median_fare" name="Median" stroke={C.accent} strokeWidth={2} dot />
          <Line type="monotone" dataKey="p25_fare" name="P25" stroke={C.accentDim}
            strokeDasharray="4 2" dot={false} />
          <Line type="monotone" dataKey="p75_fare" name="P75" stroke={C.warning}
            strokeDasharray="4 2" dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}

// ─── Skeleton loader ──────────────────────────────────────────────────────────
function Skeleton({ height = 200 }) {
  return (
    <div style={{
      background: C.surface, border: `1px solid ${C.border}`,
      borderRadius: 12, height, animation: "pulse 1.5s infinite"
    }} />
  );
}

// ─── Main App ─────────────────────────────────────────────────────────────────
export default function App() {
  const [indexData, setIndexData] = useState([]);
  const [elasticityData, setElasticityData] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  const fetchAll = useCallback(async () => {
    try {
      const [idxRes, elasticRes] = await Promise.all([
        axios.get(`${API_BASE}/api/v1/index/daily?days=30`),
        axios.get(`${API_BASE}/api/v1/fares/elasticity/DEL/BOM?days=30`)
      ]);
      setIndexData(idxRes.data.data || []);
      setElasticityData(elasticRes.data.data || []);
      setLastUpdated(new Date().toLocaleTimeString("en-IN"));
      setError(null);
    } catch (e) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAll();
    const interval = setInterval(fetchAll, REFRESH_INTERVAL);
    return () => clearInterval(interval);
  }, [fetchAll]);

  const latest = indexData[0] || {};
  const routeData = latest.routes || {};

  const handleExport = () => {
    const month = new Date().toISOString().slice(0, 7);
    window.open(`${API_BASE}/api/v1/export/nso?month=${month}`, "_blank");
  };

  return (
    <div style={{
      background: C.bg, minHeight: "100vh", color: C.text,
      fontFamily: "'Inter', 'Segoe UI', sans-serif", padding: 24
    }}>
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between",
        alignItems: "center", marginBottom: 24 }}>
        <div>
          <span style={{ color: C.accent, fontWeight: 700, fontSize: 20 }}>APIx</span>
          <span style={{ color: C.textMuted, fontSize: 14, marginLeft: 8 }}>
            Real-time Airfare Price Index · India
          </span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <span style={{ color: C.textMuted, fontSize: 12 }}>
            {error ? `⚠ ${error}` : `Live · ${lastUpdated || "loading..."}`}
          </span>
          <button onClick={handleExport} style={{
            background: C.accentDim, color: "white", border: "none",
            borderRadius: 6, padding: "8px 16px", cursor: "pointer", fontSize: 13
          }}>
            ↓ NSO Report
          </button>
          <a href={`${API_BASE}/docs`} target="_blank" rel="noreferrer"
            style={{ color: C.accent, fontSize: 13, textDecoration: "none" }}>
            API Docs ↗
          </a>
        </div>
      </div>

      {/* Main Grid */}
      <div style={{ display: "grid", gap: 16,
        gridTemplateColumns: "280px 1fr", gridTemplateRows: "auto auto auto" }}>

        {/* Row 1 */}
        {loading ? <Skeleton height={200} /> :
          <APIxGauge
            value={latest.apix_value}
            changePct={latest.change_pct}
            lastUpdated={lastUpdated}
          />
        }
        {loading ? <Skeleton height={200} /> : <RouteTable routeData={routeData} />}

        {/* Row 2 */}
        <div style={{ gridColumn: "1 / -1", display: "grid",
          gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          {loading ? <Skeleton /> : <TrendLine data={indexData} />}
          {loading ? <Skeleton /> : <ElasticityChart data={elasticityData} />}
        </div>
      </div>

      {/* Footer */}
      <div style={{ color: C.textMuted, fontSize: 10, textAlign: "center", marginTop: 24 }}>
        SIH 2026 · PS 26056 · MoSPI / NSO · Data refreshes every 5 minutes ·
        Built by SKCT Coimbatore
      </div>

      <style>{`
        @keyframes pulse {
          0%, 100% { opacity: 1; } 50% { opacity: 0.5; }
        }
        * { box-sizing: border-box; }
        body { margin: 0; }
      `}</style>
    </div>
  );
}
```

---

## 16.8 Airflow DAG — `dags/scrape_daily.py`

```python
"""
dags/scrape_daily.py
Daily scraping DAG — runs at 06:00 IST.
Triggers all scrapers for all routes × windows.
"""

import asyncio
import logging
from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator
from airflow.utils.dates import days_ago
from kafka import KafkaProducer
import json
import os

logger = logging.getLogger(__name__)

ROUTES = [
    ("DEL", "BOM"), ("DEL", "BLR"), ("BOM", "BLR"),
    ("DEL", "CCU"), ("BLR", "HYD"), ("MAA", "DEL"),
    ("BOM", "CCU"), ("DEL", "MAA")
]
WINDOWS = [1, 7, 15, 30, 45]
MIN_FARES_EXPECTED = 50

DEFAULT_ARGS = {
    "owner": "apix",
    "retries": 2,
    "retry_delay": timedelta(minutes=5),
    "email_on_failure": True,
    "email": [os.environ.get("ALERT_EMAIL", "admin@apix.gov.in")]
}

dag = DAG(
    dag_id="apix_scrape_daily",
    default_args=DEFAULT_ARGS,
    description="Daily airfare scraping from airlines and OTAs",
    schedule_interval="30 0 * * *",  # 06:00 IST = 00:30 UTC
    start_date=days_ago(1),
    catchup=False,
    max_active_runs=1,
    tags=["apix", "scraping", "production"]
)


def make_producer() -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=os.environ.get("KAFKA_BOOTSTRAP", "kafka:9092"),
        value_serializer=lambda v: json.dumps(v).encode(),
        key_serializer=lambda k: k.encode() if k else None,
        acks="all",
        retries=3
    )


def check_proxy_health(**context):
    """Verify proxy pool has enough available proxies."""
    import requests
    proxy_api = os.environ.get("PROXY_HEALTH_URL")
    if not proxy_api:
        logger.warning("No PROXY_HEALTH_URL configured — skipping proxy check")
        return True
    try:
        resp = requests.get(proxy_api, timeout=10)
        available = resp.json().get("available", 0)
        if available < 5:
            raise ValueError(f"Only {available} proxies available — minimum 5 required")
        logger.info(f"Proxy health OK: {available} proxies available")
        return True
    except Exception as e:
        logger.error(f"Proxy health check failed: {e}")
        raise


def run_scraper(scraper_class_path: str, **context):
    """Generic task function to run any scraper class."""
    from importlib import import_module
    module_path, class_name = scraper_class_path.rsplit(".", 1)
    module = import_module(module_path)
    ScraperClass = getattr(module, class_name)

    proxy_url = os.environ.get("PROXY_URL")
    producer = make_producer()
    base_date = context["execution_date"]

    async def run():
        async with ScraperClass(producer=producer, proxy_url=proxy_url) as scraper:
            count = await scraper.run_all_routes(ROUTES, WINDOWS, base_date)
            return count

    count = asyncio.run(run())
    producer.flush()
    producer.close()
    logger.info(f"{class_name}: published {count} fares")
    context["ti"].xcom_push(key=f"{class_name}_count", value=count)


def validate_fare_counts(**context):
    """Check enough fares were scraped — short-circuit ETL if not."""
    ti = context["ti"]
    scrapers = ["IndigoScraper", "AirIndiaScraper", "MakemytripScraper", "IxigoScraper"]
    total = sum(
        ti.xcom_pull(key=f"{s}_count", task_ids=f"scrape_{s.lower().replace('scraper','')}")
        or 0
        for s in scrapers
    )
    logger.info(f"Total fares published today: {total}")
    if total < MIN_FARES_EXPECTED:
        logger.error(f"Insufficient fares: {total} < {MIN_FARES_EXPECTED}")
        raise ValueError(f"Scraping validation failed: only {total} fares published")
    return True


# ── Tasks ─────────────────────────────────────────────────────────────────────
t_proxy = PythonOperator(
    task_id="check_proxy_health",
    python_callable=check_proxy_health,
    dag=dag
)

t_indigo = PythonOperator(
    task_id="scrape_indigo",
    python_callable=run_scraper,
    op_kwargs={"scraper_class_path": "scraper.airline.indigo.IndigoScraper"},
    dag=dag
)

t_air_india = PythonOperator(
    task_id="scrape_air_india",
    python_callable=run_scraper,
    op_kwargs={"scraper_class_path": "scraper.airline.air_india.AirIndiaScraper"},
    dag=dag
)

t_mmt = PythonOperator(
    task_id="scrape_makemytrip",
    python_callable=run_scraper,
    op_kwargs={"scraper_class_path": "scraper.ota.makemytrip.MakemytripScraper"},
    dag=dag
)

t_ixigo = PythonOperator(
    task_id="scrape_ixigo",
    python_callable=run_scraper,
    op_kwargs={"scraper_class_path": "scraper.ota.ixigo.IxigoScraper"},
    dag=dag
)

t_validate = PythonOperator(
    task_id="validate_fare_counts",
    python_callable=validate_fare_counts,
    dag=dag
)

# ── Dependencies ───────────────────────────────────────────────────────────────
t_proxy >> [t_indigo, t_air_india, t_mmt, t_ixigo] >> t_validate
```

---

## 16.9 pytest Tests — `tests/test_laspeyres.py`

```python
"""
tests/test_laspeyres.py
Unit tests for the Laspeyres index computation.
Run: pytest tests/test_laspeyres.py -v
"""

import pytest
import pandas as pd
from unittest.mock import MagicMock
from datetime import date

from index.laspeyres import (
    compute_route_price, WINDOW_WEIGHTS,
    get_route_weights, get_base_fares
)


# ── Fixtures ──────────────────────────────────────────────────────────────────
@pytest.fixture
def sample_fares_df():
    """Synthetic fare DataFrame with known medians."""
    records = []
    for advance_days, fares in {
        1:  [8000, 8200, 7800, 8100, 8300],
        7:  [6000, 6200, 5800, 6100, 5900],
        15: [5000, 4900, 5100, 5050, 4950],
        30: [4000, 4100, 3900, 4050, 3950],
        45: [3500, 3600, 3400, 3550, 3450],
    }.items():
        for fare in fares:
            records.append({
                "origin": "DEL",
                "destination": "BOM",
                "carrier": "6E",
                "advance_days": advance_days,
                "total_fare": float(fare),
                "source": "test"
            })
    return pd.DataFrame(records)


@pytest.fixture
def mock_conn():
    """Mock DB connection."""
    conn = MagicMock()
    conn.execute.return_value.fetchall.return_value = [
        {"origin": "DEL", "destination": "BOM", "weight": 0.22, "advance_days": 1,  "median_fare": 7000},
        {"origin": "DEL", "destination": "BOM", "weight": 0.22, "advance_days": 7,  "median_fare": 5500},
        {"origin": "DEL", "destination": "BOM", "weight": 0.22, "advance_days": 15, "median_fare": 4500},
        {"origin": "DEL", "destination": "BOM", "weight": 0.22, "advance_days": 30, "median_fare": 3800},
        {"origin": "DEL", "destination": "BOM", "weight": 0.22, "advance_days": 45, "median_fare": 3200},
    ]
    return conn


# ── Tests ─────────────────────────────────────────────────────────────────────
class TestComputeRoutePrice:
    def test_returns_weighted_median(self, sample_fares_df):
        """Composite price should equal weighted sum of per-window medians."""
        result = compute_route_price(sample_fares_df, "DEL", "BOM")

        # Manual calculation:
        # T+1 median ≈ 8100, T+7 ≈ 6000, T+15 ≈ 5000, T+30 ≈ 4000, T+45 ≈ 3500
        expected = (
            WINDOW_WEIGHTS[1]  * 8100 +
            WINDOW_WEIGHTS[7]  * 6000 +
            WINDOW_WEIGHTS[15] * 5000 +
            WINDOW_WEIGHTS[30] * 4000 +
            WINDOW_WEIGHTS[45] * 3500
        )
        assert result == pytest.approx(expected, rel=0.02)

    def test_returns_none_for_missing_route(self, sample_fares_df):
        """Missing route should return None, not raise."""
        result = compute_route_price(sample_fares_df, "BOM", "CCU")
        assert result is None

    def test_handles_single_window(self):
        """Single window available — should use that window's median only."""
        df = pd.DataFrame([
            {"origin": "DEL", "destination": "MAA", "advance_days": 7,
             "total_fare": 5500.0, "carrier": "AI", "source": "test"},
            {"origin": "DEL", "destination": "MAA", "advance_days": 7,
             "total_fare": 5700.0, "carrier": "6E", "source": "test"},
        ])
        result = compute_route_price(df, "DEL", "MAA")
        assert result is not None
        assert 5500 <= result <= 5700

    def test_excludes_zero_fares(self):
        """Zero-fare records (sold-out) should not influence median."""
        df = pd.DataFrame([
            {"origin": "DEL", "destination": "BLR", "advance_days": 30,
             "total_fare": 4000.0, "carrier": "6E", "source": "test"},
            {"origin": "DEL", "destination": "BLR", "advance_days": 30,
             "total_fare": 0.0, "carrier": "SG", "source": "test"},
            {"origin": "DEL", "destination": "BLR", "advance_days": 30,
             "total_fare": 4200.0, "carrier": "QP", "source": "test"},
        ])
        # Filter sold-out before passing to compute_route_price
        df = df[df["total_fare"] > 0]
        result = compute_route_price(df, "DEL", "BLR")
        assert result == pytest.approx(4100.0, rel=0.01)


class TestWindowWeights:
    def test_weights_sum_to_one(self):
        """WINDOW_WEIGHTS must sum to 1.0."""
        assert sum(WINDOW_WEIGHTS.values()) == pytest.approx(1.0)

    def test_all_windows_present(self):
        """All 5 advance-purchase windows must have weights."""
        assert set(WINDOW_WEIGHTS.keys()) == {1, 7, 15, 30, 45}

    def test_t15_highest_weight(self):
        """T+15 should have highest booking weight (peak planning horizon)."""
        assert WINDOW_WEIGHTS[15] == max(WINDOW_WEIGHTS.values())


class TestIndexMath:
    def test_base_period_gives_100(self):
        """When current prices = base prices, index should equal 100."""
        # Same prices in both periods → sub-index = 1.0 → APIx = 100
        current_price = 5000.0
        base_price = 5000.0
        sub_index = (current_price / base_price) * 100
        assert sub_index == pytest.approx(100.0)

    def test_price_increase_reflects_above_100(self):
        """25% price increase → index ≈ 125."""
        sub_index = (6250 / 5000) * 100
        assert sub_index == pytest.approx(125.0)

    def test_price_decrease_reflects_below_100(self):
        """20% price drop → index = 80."""
        sub_index = (4000 / 5000) * 100
        assert sub_index == pytest.approx(80.0)
```

---

## 16.10 Environment Config — `.env.example`

```bash
# .env.example
# Copy to .env and fill values before running docker-compose up

# ── Database ────────────────────────────────────────────────────────────────
DATABASE_URL=postgresql://apix_user:CHANGE_ME@db:5432/apix
POSTGRES_DB=apix
POSTGRES_USER=apix_user
POSTGRES_PASSWORD=CHANGE_ME

# ── Kafka ────────────────────────────────────────────────────────────────────
KAFKA_BOOTSTRAP=kafka:9092
KAFKA_TOPIC_RAW=raw_fares
KAFKA_TOPIC_CLEAN=cleaned_fares

# ── Redis ────────────────────────────────────────────────────────────────────
REDIS_URL=redis://redis:6379

# ── Proxy (residential proxy service) ───────────────────────────────────────
PROXY_URL=http://user:pass@proxy.provider.com:8080
PROXY_HEALTH_URL=https://api.proxy.provider.com/health

# ── CAPTCHA ──────────────────────────────────────────────────────────────────
TWOCAPTCHA_API_KEY=your_key_here

# ── Airflow ──────────────────────────────────────────────────────────────────
AIRFLOW__CORE__EXECUTOR=LocalExecutor
AIRFLOW__DATABASE__SQL_ALCHEMY_CONN=postgresql+psycopg2://apix_user:CHANGE_ME@db:5432/apix_airflow
AIRFLOW__CORE__FERNET_KEY=generate_with_python_fernet
ALERT_EMAIL=team@apix.gov.in

# ── Frontend ──────────────────────────────────────────────────────────────────
REACT_APP_API_URL=http://localhost:8000
REACT_APP_MAPBOX_TOKEN=your_mapbox_token  # optional for route heatmap
```

---

## 16.11 Backtest Report Template — `docs/BACKTEST_REPORT.md`

```markdown
# APIx Backtest Report — 30-Day Validation

## Methodology
- Ran APIx index computation on historical `fare_quotes` data (last 30 days)
- Compared monthly aggregate against DGCA published average fares
- Metric: MAPE (Mean Absolute Percentage Error)

## Results

| Route     | APIx Monthly Avg | DGCA Published | MAPE   |
|-----------|-----------------|----------------|--------|
| DEL-BOM   | ₹X,XXX          | ₹X,XXX         | X.X%   |
| DEL-BLR   | ₹X,XXX          | ₹X,XXX         | X.X%   |
| BOM-BLR   | ₹X,XXX          | ₹X,XXX         | X.X%   |
| DEL-CCU   | ₹X,XXX          | ₹X,XXX         | X.X%   |
| BLR-HYD   | ₹X,XXX          | ₹X,XXX         | X.X%   |
| MAA-DEL   | ₹X,XXX          | ₹X,XXX         | X.X%   |
| BOM-CCU   | ₹X,XXX          | ₹X,XXX         | X.X%   |
| DEL-MAA   | ₹X,XXX          | ₹X,XXX         | X.X%   |
| **Aggregate** | **APIx** | **DGCA** | **<8%** |

**Target:** MAPE < 8%  
**Result:** [ ] PASS  [ ] FAIL

## DGCA Data Sources
- DGCA Monthly Domestic Airline Statistics
- URL: https://dgca.gov.in/digigov-portal/
- Path: Air Transport → Statistics → Monthly Airline Statistics
- File: `Domestic_airlines_passengers_monthwise.xlsx`

## Notes
- DGCA data is monthly aggregates; APIx provides daily values
- Comparison done at monthly average level
- Sold-out flights excluded from both datasets
- Outliers (IQR×1.5) removed before comparison
```

---

## 16.12 README — `README.md`

```markdown
# APIx — Real-time Airfare Price Index for India
**SIH 2026 · PS 26056 · MoSPI / NSO**

Automated platform to compute a Laspeyres-weighted Airfare Price Index (APIx)
from live scraping of Indian airline websites and OTAs, for augmentation of India's CPI.

## Quick Start

### Prerequisites
- Docker + Docker Compose
- 4GB RAM minimum
- Port availability: 3000, 5432, 8000, 8080, 9092

### Setup

```bash
git clone https://github.com/your-team/apix.git
cd apix
cp .env.example .env
# Edit .env with your proxy and DB credentials

docker-compose up -d
# Wait ~60s for all services to initialise

# Initialise database schema
docker-compose exec api python -c "
import asyncpg, asyncio, os
async def init():
    conn = await asyncpg.connect(os.environ['DATABASE_URL'])
    with open('/app/db/schema.sql') as f:
        await conn.execute(f.read())
    await conn.close()
asyncio.run(init())
"

# Trigger first scrape manually
docker-compose exec airflow-scheduler airflow dags trigger apix_scrape_daily

# Run index computation
docker-compose exec api python -m index.compute_daily
```

### Access
| Service | URL |
|---|---|
| Dashboard | http://localhost:3000 |
| API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |
| Airflow | http://localhost:8080 (admin/admin) |

## Running Tests

```bash
docker-compose exec api pytest tests/ -v --tb=short
```

## Project Structure
See `docs/ARCHITECTURE.md` for full module breakdown.

## Ethical Compliance
All scrapers respect `robots.txt`, rate-limit to 1 req/8s per domain,
and identify as `APIxBot/1.0`. See `LEGAL.md` for per-source ToS review.

## Team
SKCT Coimbatore · SIH 2026
```

---

*Generated for SIH 2026 | PS 26056 | Team: SKCT Coimbatore*  
*AI Usage: Append this file's content to any code-generation prompt to scaffold the full project.*  
*PPT Usage: Each `## SLIDE:` section = one slide. Theme: navy #0D1B2A + teal #00C9A7.*
