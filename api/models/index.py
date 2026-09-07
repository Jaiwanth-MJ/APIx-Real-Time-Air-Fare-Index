"""
api/models/index.py
"""

from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class IndexMetadata(BaseModel):
    base_period: str = "2024-01-01"
    last_updated: str
    routes_count: int = 8
    source_count: int = 11

class IndexDataPoint(BaseModel):
    date: str
    apix_value: float
    change_abs: Optional[float] = None
    change_pct: Optional[float] = None
    routes: Dict[str, float] = Field(default_factory=dict)

class IndexResponse(BaseModel):
    meta: IndexMetadata
    data: List[IndexDataPoint]
