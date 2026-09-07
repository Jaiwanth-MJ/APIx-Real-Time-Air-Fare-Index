"""
api/models/fare.py & api/models/index.py
Pydantic schemas for API request validation and response serialization.
"""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field

class RouteWeight(BaseModel):
    origin: str
    destination: str
    weight: float
    dgca_rank: int

class FareQuoteSchema(BaseModel):
    id: str
    scraped_at: str
    origin: str
    destination: str
    departure_date: str
    advance_days: int
    carrier: str
    flight_number: Optional[str] = None
    fare_class: str = "E"
    base_fare: float
    taxes: float = 0.0
    udf: float = 0.0
    convenience_fee: float = 0.0
    total_fare: float
    currency: str = "INR"
    source: str
    is_outlier: bool = False
    is_sold_out: bool = False

class ElasticityPoint(BaseModel):
    advance_days: int
    p25_fare: float
    median_fare: float
    p75_fare: float
    sample_size: int

class CarrierFareSummary(BaseModel):
    carrier: str
    carrier_name: str
    avg_fare: float
    median_fare: float
    sample_count: int

class DailyIndexItem(BaseModel):
    date: str
    apix_value: float
    change_abs: Optional[float] = None
    change_pct: Optional[float] = None
    routes: Dict[str, float] = Field(default_factory=dict)

class DailyIndexResponse(BaseModel):
    meta: Dict[str, Any]
    data: List[DailyIndexItem]
