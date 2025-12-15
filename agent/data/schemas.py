"""Data schemas for validation.

Pydantic models for data validation and serialization.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal


@dataclass
class KeywordPerformance:
    """Keyword performance data schema."""
    keyword_id: str
    date: date
    impressions: int
    clicks: int
    spend: float
    sales: float
    orders: int

    def __post_init__(self):
        """Ensure numeric types are correct."""
        self.impressions = int(self.impressions)
        self.clicks = int(self.clicks)
        self.spend = float(self.spend)
        self.sales = float(self.sales)
        self.orders = int(self.orders)
