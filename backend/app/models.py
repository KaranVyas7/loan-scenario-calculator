from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

from sqlmodel import SQLModel, Field


class LoanScenario(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    amount: float
    apr: float
    term_months: int
    monthly_payment: float

    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), index=True)
