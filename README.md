# API Testing Suite

[![CI](https://github.com/leadmee/200/actions/workflows/ci.yml/badge.svg)](https://github.com/leadmee/200/actions/workflows/ci.yml)

QA Automation portfolio project that combines two deliverables in one repository:

1. **HTTP API tester** — a declarative CLI runner (a Postman/Insomnia-lite). Request
   collections are described in YAML and checked for status code, response time,
   JSON Schema conformance and JSONPath values, with variable chaining between requests.
2. **pytest test project** for the public **restful-booker** API — positive, negative
   and contract scenarios, Allure reporting, and CI on GitHub Actions.

Both parts share the same dependencies, the same JSON schemas (`shared/schemas/`) and
run against the same real API.

## Layout

```
apitester/        Part A — declarative HTTP tester (CLI)
collections/      YAML collections + environments for the tester
api_client/       Shared restful-booker client (BookingAPI)
tests/            Part B — pytest suite
shared/schemas/   JSON Schemas used by both parts
.github/workflows CI pipeline
```

## Quick start

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate   |   *nix: . .venv/bin/activate
pip install -r requirements.txt
```

### Part A — run the tester

```bash
python -m apitester run collections/booking_flow.yaml --env prod
# JSON report is written to report/result.json; non-zero exit on any failure.
```

`collections/booking_flow_failing.yaml` is intentionally broken to demonstrate the
non-zero exit code used as a CI gate.

### Part B — run the tests

```bash
pytest -q                       # everything (live API + offline unit tests)
pytest -m unit                  # offline unit tests for the tester (no network)
pytest -m smoke                 # smoke subset
pytest -m negative              # negative subset
pytest --alluredir=allure-results
allure serve allure-results     # open the Allure report (requires Allure CLI)
```

Unit tests for the tester itself live in `tests/unit/` and run without touching the
network (they use a fake HTTP client), so they are safe for fast local runs and CI.

## Target API

[restful-booker](https://restful-booker.herokuapp.com) — token auth + full CRUD over
bookings. Credentials: `admin` / `password123`. The Heroku dyno sleeps when idle, so
the first request may be slow; the suite pings it once before running.
