import allure
import pytest


@allure.feature("Booking CRUD")
@allure.title("Create then read a booking")
@pytest.mark.smoke
def test_create_and_read_booking(api, booking_factory):
    booking_id, payload = booking_factory()
    resp = api.get_booking(booking_id)
    assert resp.status_code == 200
    body = resp.json()
    assert body["firstname"] == payload["firstname"]
    assert body["lastname"] == payload["lastname"]
    assert body["totalprice"] == payload["totalprice"]


@allure.feature("Booking CRUD")
@pytest.mark.regression
@pytest.mark.parametrize(
    "firstname,lastname",
    [("Jim", "Brown"), ("Anna", "Smith"), ("Мария", "Иванова")],
)
def test_create_booking_various_names(api, booking_factory, firstname, lastname):
    booking_id, _ = booking_factory(firstname=firstname, lastname=lastname)
    resp = api.get_booking(booking_id)
    assert resp.status_code == 200
    assert resp.json()["firstname"] == firstname


@allure.feature("Booking CRUD")
@allure.title("Full update (PUT) replaces the booking")
@pytest.mark.regression
def test_update_booking(api, booking_factory, auth_token):
    booking_id, payload = booking_factory()
    payload["firstname"] = "Updated"
    payload["totalprice"] = 999
    resp = api.update_booking(booking_id, payload, auth_token)
    assert resp.status_code == 200
    body = resp.json()
    assert body["firstname"] == "Updated"
    assert body["totalprice"] == 999


@allure.feature("Booking CRUD")
@allure.title("Partial update (PATCH) changes only given fields")
@pytest.mark.regression
def test_partial_update_booking(api, booking_factory, auth_token):
    booking_id, payload = booking_factory()
    resp = api.partial_update_booking(booking_id, {"firstname": "Patched"}, auth_token)
    assert resp.status_code == 200
    body = resp.json()
    assert body["firstname"] == "Patched"
    # Untouched field must be preserved.
    assert body["lastname"] == payload["lastname"]


@allure.feature("Booking CRUD")
@allure.title("Delete removes the booking")
@pytest.mark.regression
def test_delete_booking(api, booking_factory, auth_token):
    booking_id, _ = booking_factory()
    resp = api.delete_booking(booking_id, auth_token)
    assert resp.status_code == 201
    assert api.get_booking(booking_id).status_code == 404
