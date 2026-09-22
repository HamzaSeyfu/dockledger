from __future__ import annotations

import csv
import json
from datetime import datetime
from pathlib import Path

from .models import Delivery, RingEvent


def load_deliveries(path: Path) -> list[Delivery]:
    deliveries: list[Delivery] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            deliveries.append(
                Delivery(
                    delivery_id=row["delivery_id"],
                    carrier=row["carrier"],
                    truck_ref=row["truck_ref"],
                    dock=row["dock"],
                    scheduled_start=datetime.fromisoformat(row["scheduled_start"]),
                    scheduled_end=datetime.fromisoformat(row["scheduled_end"]),
                    free_minutes=int(row["free_minutes"]),
                    detention_rate_per_hour=float(row["detention_rate_per_hour"]),
                )
            )
    return deliveries


def load_demo_events(path: Path) -> list[RingEvent]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    return [
        RingEvent(
            event_id=item["event_id"],
            device_id=item["device_id"],
            event_type=item["event_type"],
            timestamp=datetime.fromisoformat(item["timestamp"]),
            operator_tag=item.get("operator_tag"),
            raw=item,
        )
        for item in payload
    ]
