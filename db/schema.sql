-- ============================================================
-- APIx Database Schema
-- Compatible with PostgreSQL / TimescaleDB and SQLite
-- ============================================================

-- Routes basket (DGCA-weighted)
CREATE TABLE IF NOT EXISTS routes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    origin      CHAR(3) NOT NULL,
    destination CHAR(3) NOT NULL,
    weight      NUMERIC(5,4) NOT NULL,
    dgca_rank   SMALLINT,
    active      BOOLEAN DEFAULT 1,
    created_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (origin, destination)
);

-- Carriers
CREATE TABLE IF NOT EXISTS carriers (
    code        VARCHAR(10) PRIMARY KEY,  -- IATA: 6E, AI, QP, SG, I5
    name        VARCHAR(50) NOT NULL,
    active      BOOLEAN DEFAULT 1
);

-- Main fare quotes time-series table
CREATE TABLE IF NOT EXISTS fare_quotes (
    id              TEXT PRIMARY KEY,
    scraped_at      TIMESTAMP NOT NULL,
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
    is_outlier      BOOLEAN DEFAULT 0,
    is_sold_out     BOOLEAN DEFAULT 0,
    raw_payload     TEXT
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_fare_route ON fare_quotes (origin, destination, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_fare_advance ON fare_quotes (advance_days, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_fare_carrier ON fare_quotes (carrier, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_fare_scraped_at ON fare_quotes (scraped_at DESC);

-- Daily computed index
CREATE TABLE IF NOT EXISTS index_daily (
    index_date      DATE PRIMARY KEY,
    apix_value      NUMERIC(8,4) NOT NULL,
    base_period     DATE NOT NULL DEFAULT '2024-01-01',
    routes_snapshot TEXT,  -- JSON string of {route: sub_index_value}
    sample_size     INT,
    notes           TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Weekly rollup
CREATE TABLE IF NOT EXISTS index_weekly (
    week_start      DATE PRIMARY KEY,
    apix_value      NUMERIC(8,4) NOT NULL,
    mom_change_pct  NUMERIC(6,2),
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Monthly rollup (NSO-ready)
CREATE TABLE IF NOT EXISTS index_monthly (
    month_year      DATE PRIMARY KEY,  -- first of month
    apix_value      NUMERIC(8,4) NOT NULL,
    mom_change_pct  NUMERIC(6,2),
    yoy_change_pct  NUMERIC(6,2),
    routes_snapshot TEXT,
    created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- DGCA benchmark for backtest validation
CREATE TABLE IF NOT EXISTS dgca_benchmark (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    route_id    INT REFERENCES routes(id),
    month_year  DATE NOT NULL,
    avg_fare    NUMERIC(10,2) NOT NULL,
    source_url  TEXT,
    loaded_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE (route_id, month_year)
);

-- Seed: Route basket (DGCA Top 8 Domestic Routes)
INSERT OR IGNORE INTO routes (id, origin, destination, weight, dgca_rank) VALUES
    (1, 'DEL', 'BOM', 0.22, 1),
    (2, 'DEL', 'BLR', 0.18, 2),
    (3, 'BOM', 'BLR', 0.14, 3),
    (4, 'DEL', 'CCU', 0.12, 4),
    (5, 'BLR', 'HYD', 0.10, 5),
    (6, 'MAA', 'DEL', 0.09, 6),
    (7, 'BOM', 'CCU', 0.08, 7),
    (8, 'DEL', 'MAA', 0.07, 8);

-- Seed: Major Indian Carriers
INSERT OR IGNORE INTO carriers (code, name) VALUES
    ('6E', 'IndiGo'),
    ('AI', 'Air India'),
    ('QP', 'Akasa Air'),
    ('SG', 'SpiceJet'),
    ('I5', 'Air India Express');
