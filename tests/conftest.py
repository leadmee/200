"""Shared fixtures for the restful-booker test suite."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable

import pytest
from faker import Faker

from api_client.booking_api import BookingAPI

fake = Faker()
BASE_URL = "https://restful-booker.herokuapp.com"
SCHEMAS_DIR = Path(__file__).resolve().parents[1] / "shared" / "schemas"


def make_booking_payload(**overrides: Any) -> dict[str, Any]:
    """Build a valid booking body, overridable per field."""
    checkin = fake.date_between(start_date="-30d", end_date="today").isoformat()
    checkout = fake.date_between(start_date="today", end_date="+30d").isoformat()
    payload: dict[str, Any] = {
        "firstname": fake.first_name(),
        "lastname": fake.last_name(),
        "totalprice": fake.random_int(min=50, max=5000),
        "depositpaid": fake.boolean(),
        "bookingdates": {"checkin": checkin, "checkout": checkout},
        "additionalneeds": fake.random_element(["Breakfast", "Late checkout", "Extra bed"]),
    }
    payload.update(overrides)
    return payload


@pytest.fixture(scope="session")
def base_url() -> str:
    return BASE_URL


@pytest.fixture(scope="session")
def api(base_url: str) -> BookingAPI:
    client = BookingAPI(base_url)
    # Wake up the (often sleeping) Heroku dyno before the suite runs.
    try:
        client.ping()
    except Exception:
        pass
    yield client
    client.session.close()


@pytest.fixture(scope="session")
def auth_token(api: BookingAPI) -> str:
    resp = api.create_auth_token("admin", "password123")
    assert resp.status_code == 200, resp.text
    token = resp.json().get("token")
    assert token, f"no token in response: {resp.text}"
    return token


@pytest.fixture
def sample_booking_payload() -> dict[str, Any]:
    return make_booking_payload()


@pytest.fixture
def booking_factory(api: BookingAPI, auth_token: str) -> Callable[..., tuple[int, dict[str, Any]]]:
    """Create bookings and clean them up after the test."""
    created: list[int] = []

    def _create(**overrides: Any) -> tuple[int, dict[str, Any]]:
        payload = make_booking_payload(**overrides)
        resp = api.create_booking(payload)
        assert resp.status_code == 200, resp.text
        booking_id = resp.json()["bookingid"]
        created.append(booking_id)
        return booking_id, payload

    yield _create

    for booking_id in created:
        try:
            api.delete_booking(booking_id, auth_token)
        except Exception:
            pass


@pytest.fixture(scope="session")
def load_schema() -> Callable[[str], dict[str, Any]]:
    def _load(name: str) -> dict[str, Any]:
        return json.loads((SCHEMAS_DIR / name).read_text(encoding="utf-8"))

    return _load
