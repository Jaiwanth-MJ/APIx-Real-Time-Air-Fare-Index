-- ============================================================
-- APIx TimescaleDB / PostgreSQL Schema
-- Run: psql -U apix_user -d apix -f db/schema_pg.sql
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

-- Convert to hypertable if timescale is available
DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'timescaledb') THEN
        PERFORM create_hypertable('fare_quotes', 'scraped_at', if_not_exists => TRUE);
    END IF;
END $$;

-- Indexes
CREATE INDEX IF NOT EXISTS idx_fare_route ON fare_quotes (origin, destination, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_fare_advance ON fare_quotes (advance_days, scraped_at DESC);
CREATE INDEX IF NOT EXISTS idx_fare_carrier ON fare_quotes (carrier, scraped_at DESC);

-- Daily computed index
CREATE TABLE IF NOT EXISTS index_daily (
    index_date      DATE PRIMARY KEY,
    apix_value      NUMERIC(8,4) NOT NULL,
    base_period     DATE NOT NULL DEFAULT '2024-01-01',
    routes_snapshot JSONB,
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
    month_year      DATE PRIMARY KEY,
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
ON CONFLICT (origin, destination) DO UPDATE 
SET weight = EXCLUDED.weight, dgca_rank = EXCLUDED.dgca_rank;

-- Seed: Carriers
INSERT INTO carriers (code, name) VALUES
    ('6E', 'IndiGo'),
    ('AI', 'Air India'),
    ('QP', 'Akasa Air'),
    ('SG', 'SpiceJet'),
    ('I5', 'Air India Express')
ON CONFLICT (code) DO NOTHING;
