from __future__ import annotations

from datetime import datetime
from typing import Any

import requests

from .models import RingEvent

API_BASE = "https://api.amazonvision.com"


class RingAPIError(RuntimeError):
    pass


class RingClient:
    """Minimal Ring (Amazon Vision) API client.

    The endpoints mirror AmazonAppDev/ring-api-helloworld, the canonical
    starter linked by the Amazon Developer Hackathon resources page.
    """

    def __init__(self, access_token: str, timeout: float = 15.0):
        if not access_token:
            raise ValueError("A Ring access token is required")
        self.access_token = access_token
        self.timeout = timeout

    @property
    def headers(self) -> dict[str, str]:
        return {"Authorization": f"Bearer {self.access_token}"}

    def _get(self, path: str, params: dict[str, Any] | None = None) -> dict:
        url = f"{API_BASE}{path}"
        try:
            response = requests.get(
                url,
                headers=self.headers,
                params=params or {},
                timeout=self.timeout,
            )
            response.raise_for_status()
        except requests.RequestException as exc:
            raise RingAPIError(f"Ring API request failed: {exc}") from exc
        return response.json()

    def list_devices(self) -> dict:
        return self._get("/v1/devices")

    def event_history(self, device_id: str, event_types: str | None = None) -> dict:
        params = {"event_types": event_types} if event_types else None
        return self._get(f"/v1/history/devices/{device_id}/events", params=params)


def normalize_event_history(payload: dict, device_id: str) -> list[RingEvent]:
    events: list[RingEvent] = []
    for item in payload.get("data", []):
        attrs = item.get("attributes", {})
        timestamp = attrs.get("start")
        if not timestamp:
            continue
        normalized = timestamp.replace("Z", "+00:00")
        events.append(
            RingEvent(
                event_id=str(item.get("id", f"ring-{len(events)+1}")),
                device_id=device_id,
                event_type=str(attrs.get("event_type", "unknown")),
                timestamp=datetime.fromisoformat(normalized),
                raw=item,
            )
        )
    return sorted(events, key=lambda event: event.timestamp)
