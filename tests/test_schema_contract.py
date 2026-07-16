import allure
import jsonschema
import pytest


@allure.feature("Contract")
@allure.title("Auth response matches its JSON Schema")
@pytest.mark.contract
def test_auth_response_schema(api, load_schema):
    resp = api.create_auth_token("admin", "password123")
    jsonschema.validate(resp.json(), load_schema("auth_token.json"))


@allure.feature("Contract")
@allure.title("Create-booking response matches its JSON Schema")
@pytest.mark.contract
def test_create_response_schema(api, auth_token, sample_booking_payload, load_schema):
    resp = api.create_booking(sample_booking_payload)
    assert resp.status_code == 200
    jsonschema.validate(resp.json(), load_schema("booking_created.json"))
    api.delete_booking(resp.json()["bookingid"], auth_token)


@allure.feature("Contract")
@allure.title("Get-booking response matches the booking JSON Schema")
@pytest.mark.contract
def test_get_booking_schema(api, booking_factory, load_schema):
    booking_id, _ = booking_factory()
    resp = api.get_booking(booking_id)
    assert resp.status_code == 200
    jsonschema.validate(resp.json(), load_schema("booking.json"))
