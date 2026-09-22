from __future__ import annotations

from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass(frozen=True)
class Delivery:
    delivery_id: str
    carrier: str
    truck_ref: str
    dock: str
    scheduled_start: datetime
    scheduled_end: datetime
    free_minutes: int = 60
    detention_rate_per_hour: float = 75.0


@dataclass(frozen=True)
class RingEvent:
    event_id: str
    device_id: str
    event_type: str
    timestamp: datetime
    operator_tag: str | None = None
    raw: dict | None = None


@dataclass(frozen=True)
class VisitEvidence:
    delivery_id: str
    arrival_event_id: str
    departure_event_id: str
    arrival_at: datetime
    departure_at: datetime
    dwell_minutes: int
    free_minutes: int
    billable_minutes: int
    estimated_detention: float
    review_status: str = "human_confirmed"

    def to_dict(self) -> dict:
        data = asdict(self)
        data["arrival_at"] = self.arrival_at.isoformat()
        data["departure_at"] = self.departure_at.isoformat()
        return data


@dataclass(frozen=True)
class InvoiceComparison:
    delivery_id: str
    claimed_minutes: int
    claimed_amount: float
    evidence_minutes: int
    evidence_amount: float
    minute_delta: int
    amount_delta: float
    verdict: str

    def to_dict(self) -> dict:
        return asdict(self)
