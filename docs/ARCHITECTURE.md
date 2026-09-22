# DockLedger architecture

```text
Delivery schedule CSV
        │
        ▼
Appointment model ──────────────┐
                                │
Ring Partner API                │
GET /v1/devices                 │
GET /v1/history/devices/{id}/events
        │                       │
        ▼                       │
Candidate event window          │
        │                       │
        ▼                       │
Human arrival/departure review ◄┘
        │
        ▼
Dwell + free-time calculation
        │
        ▼
Detention estimate
        │
        ▼
Invoice reconciliation
        │
        ▼
Auditable evidence record
```

## Design decisions

- **Evidence before automation.** Motion events are useful evidence but are not treated as perfect truck identity detection.
- **Human confirmation is explicit.** The MVP asks an operator to confirm arrival/departure candidates before a charge is calculated.
- **Ring is a runtime integration.** `dockledger.ring.RingClient` calls the Ring (Amazon Vision) API directly.
- **Synthetic demo data is separated from live API data.** Reviewers can run the workflow without credentials and can plug in a Ring Developer Playground token for the real API path.
- **No secrets in source control.** Ring tokens are loaded from `RING_ACCESS_TOKEN`.
