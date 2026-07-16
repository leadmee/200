import allure
import pytest


@allure.feature("Health")
@allure.title("GET /ping returns 201")
@pytest.mark.smoke
def test_ping(api):
    resp = api.ping()
    assert resp.status_code == 201
