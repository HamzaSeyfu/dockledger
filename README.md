# DockLedger

**Ring-powered evidence for warehouse detention and invoice disputes.**

DockLedger is a submission-in-progress for the **Build, Ship, Shape: Amazon Developer Hackathon**, primary track **Ring**, category **Business Systems**.

A warehouse appointment says when a truck was expected. A detention invoice says how long it waited. DockLedger adds a third source: timestamped Ring events at the dock. It narrows the event window around the appointment, lets an operator confirm arrival and departure evidence, calculates dwell/free/billable time, and compares the result with the carrier's detention claim.

> Status: **MVP v0.1**. The repository contains a runnable synthetic demo and real Ring Partner API calls. The next milestone is wiring live/simulated Ring events into the browser review flow for the final hackathon demo.

## What works now

- Importable delivery schedule model with free-time and detention-rate rules.
- **Real Ring API integration** for device discovery and event history using `https://api.amazonvision.com`.
- Normalization of Ring event-history responses into DockLedger evidence objects.
- Candidate-event filtering around a scheduled dock appointment.
- Human-reviewed arrival/departure pairing.
- Dwell-time, billable-time, and estimated detention calculation.
- Invoice reconciliation with a clear `consistent` / `review_required` verdict.
- FastAPI backend, browser demo, automated tests, and GitHub Actions CI.

## Why human review?

The first MVP intentionally does **not** pretend that every Ring motion event uniquely identifies a truck. Ring evidence narrows the time window; an operator confirms the arrival/departure pair before DockLedger creates an auditable charge record. This keeps the current behavior explainable and avoids overclaiming computer-vision capability we have not built yet.

## Ring integration

The hackathon's canonical starter is [`AmazonAppDev/ring-api-helloworld`](https://github.com/AmazonAppDev/ring-api-helloworld). DockLedger uses the same Ring (Amazon Vision) runtime endpoints:

```text
GET https://api.amazonvision.com/v1/devices
GET https://api.amazonvision.com/v1/history/devices/{device_id}/events
```

Implementation: [`src/dockledger/ring.py`](src/dockledger/ring.py)

### Try with a real Ring Developer token

1. Get a short-lived token from the Ring Developer Playground.
2. Set it locally:

```bash
export RING_ACCESS_TOKEN='eyJ...'
```

3. Run DockLedger and call:

```bash
curl http://localhost:8000/api/ring/devices
curl http://localhost:8000/api/ring/events/<device-id>
```

No access token is committed to this repository.

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -e '.[dev]'
uvicorn dockledger.api:app --reload
```

Open `http://localhost:8000`.

The browser demo uses synthetic delivery/event data so it can be reviewed without Ring credentials.

## Test

```bash
pytest -q
```

## Current demo scenario

- Appointment: **Dock 4, 08:00–09:00**
- Confirmed arrival event: **07:53**
- Confirmed departure event: **09:41**
- Dwell: **108 min**
- Free time: **60 min**
- Billable detention: **48 min**
- Rate: **$90/hour**
- Evidence estimate: **$72.00**

Edit the claimed minutes/amount in the UI to see when the invoice becomes a review case.

## Architecture

See [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

```text
Schedule → Ring event history → candidate window → human confirmation
        → dwell/free/billable time → detention estimate → invoice comparison
```

## Hackathon roadmap

- [x] Public open-source repository and license
- [x] Core detention/reconciliation engine
- [x] Runtime Ring API client
- [x] Synthetic browser demo
- [x] Tests + CI
- [ ] Feed live/simulated Ring events directly into the review UI
- [ ] CSV upload for multiple appointments/invoices
- [ ] Evidence packet export (JSON/PDF)
- [ ] Final Ring simulator/device capture for the <3 minute demo video
- [ ] Optional AWS Builder layer only after a real AWS service is integrated

## Open Source mini-challenge evidence

Alongside DockLedger, I also contributed a reliability/human-review layer to an AWS healthcare-agent sample during the hackathon window:

- Contribution: https://github.com/HamzaSeyfu/sample-healthcare-agents/pull/1
- Public repository: https://github.com/HamzaSeyfu/sample-healthcare-agents

## License

MIT. See [`LICENSE`](LICENSE).
