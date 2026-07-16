import allure
import pytest


@allure.feature("Auth")
@allure.title("Valid credentials return a token")
@pytest.mark.smoke
def test_auth_returns_token(api):
    resp = api.create_auth_token("admin", "password123")
    assert resp.status_code == 200
    assert resp.json().get("token")


@allure.feature("Auth")
@allure.title("Invalid credentials are rejected without a token")
@pytest.mark.negative
def test_auth_bad_credentials(api):
    resp = api.create_auth_token("admin", "wrong-password")
    # restful-booker answers 200 with a reason instead of issuing a token.
    assert resp.status_code == 200
    body = resp.json()
    assert "token" not in body
    assert body.get("reason") == "Bad credentials"
