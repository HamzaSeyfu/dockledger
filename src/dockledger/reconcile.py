from __future__ import annotations

from datetime import timedelta

from .models import Delivery, InvoiceComparison, RingEvent, VisitEvidence


def suggest_candidate_events(
    delivery: Delivery,
    events: list[RingEvent],
    before_minutes: int = 120,
    after_minutes: int = 240,
) -> list[RingEvent]:
    """Return Ring events close enough to a scheduled dock appointment.

    DockLedger deliberately keeps arrival/departure confirmation human-reviewed:
    Ring motion evidence narrows the window, while an operator confirms which
    events correspond to the truck visit.
    """
    lower = delivery.scheduled_start - timedelta(minutes=before_minutes)
    upper = delivery.scheduled_end + timedelta(minutes=after_minutes)
    return [event for event in events if lower <= event.timestamp <= upper]


def build_visit_evidence(
    delivery: Delivery,
    arrival_event: RingEvent,
    departure_event: RingEvent,
) -> VisitEvidence:
    if departure_event.timestamp <= arrival_event.timestamp:
        raise ValueError("Departure must be after arrival")

    dwell_minutes = int((departure_event.timestamp - arrival_event.timestamp).total_seconds() // 60)
    billable_minutes = max(0, dwell_minutes - delivery.free_minutes)
    estimated_detention = round(
        (billable_minutes / 60.0) * delivery.detention_rate_per_hour,
        2,
    )
    return VisitEvidence(
        delivery_id=delivery.delivery_id,
        arrival_event_id=arrival_event.event_id,
        departure_event_id=departure_event.event_id,
        arrival_at=arrival_event.timestamp,
        departure_at=departure_event.timestamp,
        dwell_minutes=dwell_minutes,
        free_minutes=delivery.free_minutes,
        billable_minutes=billable_minutes,
        estimated_detention=estimated_detention,
    )


def compare_invoice(
    evidence: VisitEvidence,
    claimed_minutes: int,
    claimed_amount: float,
    amount_tolerance: float = 5.0,
    minute_tolerance: int = 5,
) -> InvoiceComparison:
    minute_delta = claimed_minutes - evidence.billable_minutes
    amount_delta = round(claimed_amount - evidence.estimated_detention, 2)
    consistent = abs(minute_delta) <= minute_tolerance and abs(amount_delta) <= amount_tolerance
    verdict = "consistent" if consistent else "review_required"
    return InvoiceComparison(
        delivery_id=evidence.delivery_id,
        claimed_minutes=claimed_minutes,
        claimed_amount=round(claimed_amount, 2),
        evidence_minutes=evidence.billable_minutes,
        evidence_amount=evidence.estimated_detention,
        minute_delta=minute_delta,
        amount_delta=amount_delta,
        verdict=verdict,
    )
