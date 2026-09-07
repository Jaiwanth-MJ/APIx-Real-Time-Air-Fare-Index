"""
etl/decomposer.py
Fare breakdown decomposition into base fare, fuel surcharge, UDF, convenience fee, and GST.
"""

from typing import Dict

def decompose_fare(total_fare: float, is_direct: bool = True) -> Dict[str, float]:
    """Decomposes a lump-sum fare into estimated MoSPI-compliant components."""
    base_fare = round(total_fare * 0.68, 2)
    udf = 450.0
    convenience_fee = 0.0 if is_direct else 350.0
    taxes = max(0.0, round(total_fare - base_fare - udf - convenience_fee, 2))

    return {
        "base_fare": base_fare,
        "taxes": taxes,
        "udf": udf,
        "convenience_fee": convenience_fee,
        "total_fare": total_fare
    }
