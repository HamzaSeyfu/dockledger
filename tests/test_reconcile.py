from datetime import datetime

from dockledger.models import Delivery, RingEvent
from dockledger.reconcile import build_visit_evidence, compare_invoice, suggest_candidate_events


def test_build_visit_and_detention():
    delivery = Delivery(
        delivery_id="D-1",
        carrier="Carrier",
        truck_ref="TRK-1",
        dock="Dock 1",
        scheduled_start=datetime.fromisoformat("2026-09-22T08:00:00+00:00"),
        scheduled_end=datetime.fromisoformat("2026-09-22T09:00:00+00:00"),
        free_minutes=60,
        detention_rate_per_hour=90,
    )
    arrival = RingEvent("a", "cam", "motion.human", datetime.fromisoformat("2026-09-22T07:53:00+00:00"))
    departure = RingEvent("d", "cam", "motion.human", datetime.fromisoformat("2026-09-22T09:41:00+00:00"))

    visit = build_visit_evidence(delivery, arrival, departure)
    assert visit.dwell_minutes == 108
    assert visit.billable_minutes == 48
    assert visit.estimated_detention == 72.0


def test_invoice_mismatch_requires_review():
    delivery = Delivery(
        delivery_id="D-1",
        carrier="Carrier",
        truck_ref="TRK-1",
        dock="Dock 1",
        scheduled_start=datetime.fromisoformat("2026-09-22T08:00:00+00:00"),
        scheduled_end=datetime.fromisoformat("2026-09-22T09:00:00+00:00"),
        free_minutes=60,
        detention_rate_per_hour=90,
    )
    arrival = RingEvent("a", "cam", "motion.human", datetime.fromisoformat("2026-09-22T08:00:00+00:00"))
    departure = RingEvent("d", "cam", "motion.human", datetime.fromisoformat("2026-09-22T10:00:00+00:00"))
    visit = build_visit_evidence(delivery, arrival, departure)
    comparison = compare_invoice(visit, claimed_minutes=120, claimed_amount=180)
    assert comparison.verdict == "review_required"
    assert comparison.minute_delta == 60


def test_candidate_window_filters_noise():
    delivery = Delivery(
        delivery_id="D-1",
        carrier="Carrier",
        truck_ref="TRK-1",
        dock="Dock 1",
        scheduled_start=datetime.fromisoformat("2026-09-22T08:00:00+00:00"),
        scheduled_end=datetime.fromisoformat("2026-09-22T09:00:00+00:00"),
    )
    near = RingEvent("near", "cam", "motion.human", datetime.fromisoformat("2026-09-22T07:30:00+00:00"))
    far = RingEvent("far", "cam", "motion.human", datetime.fromisoformat("2026-09-21T20:00:00+00:00"))
    assert [event.event_id for event in suggest_candidate_events(delivery, [near, far])] == ["near"]
