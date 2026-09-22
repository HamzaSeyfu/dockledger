from dockledger.ring import normalize_event_history


def test_normalize_ring_event_history():
    payload = {
        "data": [
            {
                "id": "evt-1",
                "attributes": {
                    "event_type": "motion.human",
                    "start": "2026-09-22T08:01:00Z",
                },
            }
        ]
    }
    events = normalize_event_history(payload, "camera-1")
    assert len(events) == 1
    assert events[0].event_id == "evt-1"
    assert events[0].device_id == "camera-1"
    assert events[0].event_type == "motion.human"
