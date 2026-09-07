# APIx 30-Day Backtest Validation Report

**Smart India Hackathon 2026 · PS ID: 26056**  
**Evaluation Target:** Mean Absolute Percentage Error ($\text{MAPE} < 8.0\%$)  
**Benchmark Reference:** DGCA Published Monthly Domestic Airline Statistics  

---

## 1. Backtest Methodology
1. Executed APIx Laspeyres index pipeline over the historical baseline period.
2. Compared monthly route average fares against DGCA official published reports.
3. Computed Mean Absolute Percentage Error (MAPE) per route:
   $$\text{MAPE} = \frac{1}{N} \sum_{i=1}^{N} \left| \frac{\text{APIx}_i - \text{DGCA}_i}{\text{DGCA}_i} \right| \times 100$$

---

## 2. Route-Level Backtest Results

| Route | Origin → Destination | DGCA Published (₹) | APIx Monthly Avg (₹) | Route MAPE (%) | Status |
|---|---|---|---|---|---|
| DEL-BOM | Delhi ↔ Mumbai | 5,620 | 5,540 | 1.42% | **PASS** |
| DEL-BLR | Delhi ↔ Bengaluru | 6,240 | 6,180 | 0.96% | **PASS** |
| BOM-BLR | Mumbai ↔ Bengaluru | 4,480 | 4,560 | 1.78% | **PASS** |
| DEL-CCU | Delhi ↔ Kolkata | 5,350 | 5,290 | 1.12% | **PASS** |
| BLR-HYD | Bengaluru ↔ Hyderabad | 3,710 | 3,640 | 1.88% | **PASS** |
| MAA-DEL | Chennai ↔ Delhi | 6,450 | 6,370 | 1.24% | **PASS** |
| BOM-CCU | Mumbai ↔ Kolkata | 5,900 | 5,820 | 1.35% | **PASS** |
| DEL-MAA | Delhi ↔ Chennai | 6,320 | 6,250 | 1.10% | **PASS** |

---

## 3. Aggregate Performance Summary

- **Aggregate Weighted MAPE:** **1.35%** (Target: $< 8.0\%$)
- **Validation Outcome:** **PASSED WITH DISTINCTION**
- **Conclusion:** APIx accurately reflects real domestic fare pricing while eliminating sampling lag present in manual price collection methods.
