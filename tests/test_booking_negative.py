import allure
import pytest


@allure.feature("Booking negative")
@allure.title("Reading a non-existent booking returns 404")
@pytest.mark.negative
def test_get_nonexistent_booking(api):
    resp = api.get_booking(99_999_999)
    assert resp.status_code == 404


@allure.feature("Booking negative")
@pytest.mark.negative
@pytest.mark.parametrize("bad_id", [0, -1, 99_999_999])
def test_get_invalid_ids(api, bad_id):
    resp = api.get_booking(bad_id)
    assert resp.status_code == 404


@allure.feature("Booking negative")
@allure.title("Update without a valid token is forbidden (403)")
@pytest.mark.negative
def test_update_without_token(api, booking_factory):
    booking_id, payload = booking_factory()
    resp = api.update_booking(booking_id, payload, token="invalid-token")
    assert resp.status_code == 403


@allure.feature("Booking negative")
@allure.title("Deleting without a token is forbidden (403)")
@pytest.mark.negative
def test_delete_without_token(api, booking_factory):
    booking_id, _ = booking_factory()
    resp = api.delete_booking(booking_id, token="invalid-token")
    assert resp.status_code == 403


@allure.feature("Booking negative")
@allure.title("Creating a booking with missing required fields fails")
@pytest.mark.negative
def test_create_booking_missing_fields(api):
    resp = api.create_booking({"firstname": "OnlyName"})
    # restful-booker cannot build the record and errors out.
    assert resp.status_code >= 400
