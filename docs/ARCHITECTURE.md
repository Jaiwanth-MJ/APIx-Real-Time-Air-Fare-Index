# APIx Platform Architecture Deep-Dive

## 1. System Layers & Data Flow
The APIx architecture is structured into 6 modular layers:

### Layer 1: Data Ingestion & Scraping
- **Engines:** Playwright (Chromium) & Scrapy.
- **Coverage:** 5 domestic carriers + 6 major OTAs.
- **Anti-Bot & Stealth:** Header randomization via `fake-useragent`, canvas fingerprint masking, residential proxy rotator, and token-bucket rate limiter.
- **Ethical Middleware:** Enforces `robots.txt` disallows with 24-hour rule caching.

### Layer 2: ETL Pipeline & Outlier Filtering
- **Parser:** Extracts origin, destination, carrier, flight number, advance booking days, total fare, base fare, taxes, and fees.
- **Deduplication:** Merges identical flights queried across multiple OTAs, keeping the minimum price while preserving the provenance source.
- **IQR Outlier Filter:**
  $$\text{IQR} = Q_3 - Q_1$$
  $$\text{Lower Bound} = Q_1 - 1.5 \times \text{IQR}, \quad \text{Upper Bound} = Q_3 + 1.5 \times \text{IQR}$$
  Quotes outside this range are flagged with `is_outlier = TRUE` rather than discarded.
- **Fare Decomposition:** Separates base fare, GST (5%), fuel surcharges, User Development Fee (UDF), and convenience charges.

### Layer 3: Storage & Index Aggregation Layer
- **TimescaleDB / SQLite:** Relational storage with time-series hypertable partitioning on `scraped_at`.
- **Redis:** Sub-millisecond caching for high-frequency index and elasticity queries.

### Layer 4: Laspeyres Index Engine
- **Laspeyres Index Formula:**
  $$\text{APIx}(t) = \sum_{r=1}^{8} \left[ w_r \times \left( \frac{P_{r,t}}{P_{r,\text{base}}} \right) \right] \times 100$$
- **Advance Purchase Composite Price:**
  $$P_{r,t} = 0.10 P(T+1) + 0.20 P(T+7) + 0.30 P(T+15) + 0.25 P(T+30) + 0.15 P(T+45)$$

### Layer 5: Backend REST API
- Built with FastAPI for async non-blocking I/O.
- Exposes daily, weekly, and monthly indices, route elasticity curves, and CSV export.

### Layer 6: React Dashboard
- Built with React 18, Vite, Tailwind CSS, Recharts, and custom SVG India flight route map.
