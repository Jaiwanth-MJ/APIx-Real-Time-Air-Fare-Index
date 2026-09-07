# APIx Legal & Ethical Scraping Compliance Document

**Smart India Hackathon 2026 · PS ID: 26056**  
**Ministry:** Ministry of Statistics and Programme Implementation (MoSPI / NSO)  
**System:** APIx — Automated Real-Time Airfare Price Index Platform  

---

## 1. Executive Summary
The APIx platform adheres to strict ethical scraping guidelines, data protection standards, and Indian legal frameworks. It is designed solely for public inflation monitoring (CPI augmentation) and macroeconomic statistics under the authority of MoSPI and the Reserve Bank of India (RBI).

---

## 2. Ethical Scraping Principles

| Requirement | Implementation in APIx | Technical Enforcement |
|---|---|---|
| **robots.txt Compliance** | Strict adherence to robots.txt disallow rules across all airline and OTA domains | `scraper/middleware/robots_checker.py` caches rules and blocks disallowed paths |
| **Polite Rate Limiting** | 1 request per 8 seconds per domain (token bucket) | `scraper/middleware/rate_limiter.py` enforces domain-level throttles |
| **Transparent Bot Identification** | User-Agent specifies Government of India research intent and contact info | `APIxBot/1.0 (NSO India; contact@apix.gov.in)` header sent with all requests |
| **No Credential Access** | Only public-facing search result fares are collected | Zero authentication / login bypassing |
| **Zero PII Collection** | No user sessions, personal data, or booking identities collected | Purely aggregated price quotes and flight metadata |
| **Data Minimisation & Retention** | Raw HTML payloads deleted after 90 days; only aggregated statistics retained | Scheduled vacuuming and partitioned hypertable lifecycle |

---

## 3. Per-Source Review Matrix

| Source Domain | Source Type | robots.txt Path Check | Rate Limit | Status |
|---|---|---|---|---|
| `www.goindigo.in` | Airline Direct | Verified `/flights/*` allowed | 1 req / 8s | COMPLIANT |
| `www.airindia.com` | Airline Direct | Public booking search checked | 1 req / 8s | COMPLIANT |
| `www.akasaair.com` | Airline Direct | Public fare tables | 1 req / 8s | COMPLIANT |
| `www.spicejet.com` | Airline Direct | Flight search endpoints | 1 req / 8s | COMPLIANT |
| `www.airindiaexpress.com` | Airline Direct | Low-cost fare search | 1 req / 8s | COMPLIANT |
| `www.makemytrip.com` | OTA Aggregator | Standard public search routes | 1 req / 8s | COMPLIANT |
| `www.yatra.com` | OTA Aggregator | Standard public search routes | 1 req / 8s | COMPLIANT |
| `www.ixigo.com` | OTA Aggregator | Standard public search routes | 1 req / 8s | COMPLIANT |
| `www.easemytrip.com` | OTA Aggregator | Standard public search routes | 1 req / 8s | COMPLIANT |
| `www.cleartrip.com` | OTA Aggregator | Standard public search routes | 1 req / 8s | COMPLIANT |
| `www.goibibo.com` | OTA Aggregator | Standard public search routes | 1 req / 8s | COMPLIANT |

---

## 4. Legal Precedents & Public Interest
- Collection of publicly available price quotes for macroeconomic statistical estimation has been recognized internationally (e.g., US BLS Billion Prices Project, Eurostat Web-Scraping Guidelines for CPI).
- No copyrightable creative content is extracted; factual price quotes are utilized purely for index calculation.
