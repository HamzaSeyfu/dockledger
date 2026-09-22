# Devpost draft — DockLedger

> Working draft for the **Build, Ship, Shape: Amazon Developer Hackathon**.
> Primary track: **Ring** · Priority category: **Business Systems**

## Inspiration

Truck detention is a surprisingly expensive warehouse problem. A scheduled dock appointment records when a truck was expected, while a carrier invoice records how long it claims the truck waited. When those records disagree, operations teams often lack a neutral, timestamped evidence trail.

DockLedger explores a simple idea: use Ring events at a warehouse dock as an additional source of operational evidence, then keep the final arrival/departure confirmation human-reviewed before calculating detention time.

## What it does

DockLedger combines:

1. a scheduled delivery window;
2. timestamped Ring event history;
3. human confirmation of the arrival and departure evidence;
4. configurable free-time and detention-rate rules; and
5. the detention invoice submitted by the carrier.

It then produces an auditable visit record containing:

- confirmed arrival and departure timestamps;
- total dwell time;
- free time;
- billable detention minutes;
- expected detention cost;
- the original Ring event IDs used as evidence; and
- a reconciliation verdict: `consistent` or `review_required`.

The current browser demo can run entirely on synthetic data. The backend also contains a real Ring Partner API runtime integration for device discovery and event history.

## How we built it

The project is written in Python with a FastAPI backend.

The Ring integration follows the official Amazon Developer starter and calls the Ring (Amazon Vision) API at runtime:

```text
GET https://api.amazonvision.com/v1/devices
GET https://api.amazonvision.com/v1/history/devices/{device_id}/events
```

Ring event-history responses are normalized into DockLedger evidence objects. The reconciliation engine filters events around a scheduled appointment, waits for human arrival/departure confirmation, calculates dwell and billable detention time, and compares the result against a claimed invoice.

The repository includes:

- FastAPI REST endpoints;
- a lightweight browser interface;
- synthetic sample delivery and Ring event data;
- a Ring API client;
- detention and invoice-reconciliation logic;
- unit tests;
- GitHub Actions CI;
- an MIT license; and
- architecture documentation.

## Why human confirmation matters

The MVP deliberately does not claim that a generic Ring motion event uniquely identifies a specific truck. Instead, Ring narrows the evidence window and a human confirms the arrival/departure pair before DockLedger generates a charge record.

That design keeps the evidence explainable and prevents the hackathon demo from pretending a computer-vision capability exists before it has actually been implemented.

## Challenges

The main design challenge is turning camera events into useful business evidence without overclaiming what the event metadata can prove.

The project therefore separates:

- **raw Ring evidence**;
- **candidate-event selection**;
- **human confirmation**; and
- **deterministic financial calculation**.

A second challenge is making the project reviewable without requiring judges to own a Ring device. The local demo uses synthetic data, while the runtime Ring API integration is kept separate and can be exercised with a Ring Developer Playground token.

## Accomplishments that we're proud of

- Built the first working detention-reconciliation flow from schedule to evidence record.
- Added direct Ring API calls instead of only mentioning Ring in the README.
- Kept arrival/departure verification human-reviewed and auditable.
- Added an interactive browser demo with no frontend build system.
- Added tests and CI from the first MVP.
- Kept secrets out of source control through environment-based token handling.

## What we learned

A useful device integration is not only about collecting more data. The harder problem is deciding what that data is allowed to prove.

For DockLedger, Ring timestamps are strong evidence of activity at a dock, but the business workflow still benefits from human confirmation before those timestamps become financial evidence.

## What's next

Before final submission:

- connect live or official simulated Ring events directly into the browser review UI;
- add CSV upload for multiple appointments and invoices;
- export an evidence packet for disputes;
- improve the operator review experience;
- record the final Ring simulator/device workflow for the public demo video under three minutes;
- optionally add an AWS service only if it contributes real functionality to the product.

## Built With

- Python
- FastAPI
- Ring Partner API / Amazon Vision API
- Requests
- Pydantic
- HTML / CSS / JavaScript
- Pytest
- GitHub Actions
- GitHub

## Try it out

**Repository**

https://github.com/HamzaSeyfu/dockledger

**Run locally**

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e '.[dev]'
uvicorn dockledger.api:app --reload
```

Then open:

`http://localhost:8000`

For live Ring API calls, generate a short-lived token in the Ring Developer Playground and set:

```bash
export RING_ACCESS_TOKEN='eyJ...'
```

Then use:

```bash
curl http://localhost:8000/api/ring/devices
curl http://localhost:8000/api/ring/events/<device-id>
```

## Track

**Ring**

Priority category: **Business Systems**

## Open Source mini-challenge

A separate open-source contribution made during the hackathon window is available here:

- Contribution PR: https://github.com/HamzaSeyfu/sample-healthcare-agents/pull/1
- Repository: https://github.com/HamzaSeyfu/sample-healthcare-agents
- GitHub username: **HamzaSeyfu**

The contribution adds deterministic reliability gates, human-review escalation, tests, CI, and a public interactive demo to an AWS healthcare prior-authorization agent workflow.

## Submission status

Current repository status: **working MVP in active development**.

The final hackathon submission still needs the required Ring simulator/device demonstration video and final product-feedback fields.
