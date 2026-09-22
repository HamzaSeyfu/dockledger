from __future__ import annotations

import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from .io import load_deliveries, load_demo_events
from .models import Delivery, RingEvent
from .reconcile import build_visit_evidence, compare_invoice, suggest_candidate_events
from .ring import RingAPIError, RingClient, normalize_event_history

ROOT = Path(__file__).resolve().parents[2]
app = FastAPI(title="DockLedger", version="0.1.0")


class EvidenceSelection(BaseModel):
    delivery_id: str
    arrival_event_id: str
    departure_event_id: str
    claimed_minutes: int = Field(ge=0)
    claimed_amount: float = Field(ge=0)


def _demo_data() -> tuple[list[Delivery], list[RingEvent]]:
    deliveries = load_deliveries(ROOT / "data" / "sample_deliveries.csv")
    events = load_demo_events(ROOT / "data" / "sample_ring_events.json")
    return deliveries, events


@app.get("/")
def index():
    return FileResponse(ROOT / "static" / "index.html")


@app.get("/health")
def health():
    return {"status": "ok", "project": "DockLedger", "version": "0.1.0"}


@app.get("/api/demo")
def demo_dataset():
    deliveries, events = _demo_data()
    delivery = deliveries[0]
    candidates = suggest_candidate_events(delivery, events)
    return {
        "delivery": {
            **delivery.__dict__,
            "scheduled_start": delivery.scheduled_start.isoformat(),
            "scheduled_end": delivery.scheduled_end.isoformat(),
        },
        "candidate_events": [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
                "operator_tag": event.operator_tag,
            }
            for event in candidates
        ],
    }


@app.post("/api/reconcile")
def reconcile(selection: EvidenceSelection):
    deliveries, events = _demo_data()
    delivery = next((item for item in deliveries if item.delivery_id == selection.delivery_id), None)
    if not delivery:
        raise HTTPException(status_code=404, detail="Delivery not found")
    by_id = {event.event_id: event for event in events}
    try:
        arrival = by_id[selection.arrival_event_id]
        departure = by_id[selection.departure_event_id]
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=f"Event not found: {exc.args[0]}") from exc

    evidence = build_visit_evidence(delivery, arrival, departure)
    invoice = compare_invoice(
        evidence,
        claimed_minutes=selection.claimed_minutes,
        claimed_amount=selection.claimed_amount,
    )
    return {"visit_evidence": evidence.to_dict(), "invoice_comparison": invoice.to_dict()}


@app.get("/api/ring/devices")
def ring_devices():
    token = os.getenv("RING_ACCESS_TOKEN")
    if not token:
        raise HTTPException(
            status_code=503,
            detail="Set RING_ACCESS_TOKEN from the Ring Developer Playground to call the live Ring API.",
        )
    try:
        return RingClient(token).list_devices()
    except RingAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@app.get("/api/ring/events/{device_id}")
def ring_events(device_id: str, event_types: str | None = None):
    token = os.getenv("RING_ACCESS_TOKEN")
    if not token:
        raise HTTPException(
            status_code=503,
            detail="Set RING_ACCESS_TOKEN from the Ring Developer Playground to call the live Ring API.",
        )
    try:
        payload = RingClient(token).event_history(device_id, event_types)
        normalized = normalize_event_history(payload, device_id)
    except RingAPIError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return {
        "device_id": device_id,
        "events": [
            {
                "event_id": event.event_id,
                "event_type": event.event_type,
                "timestamp": event.timestamp.isoformat(),
            }
            for event in normalized
        ],
        "raw": payload,
    }
