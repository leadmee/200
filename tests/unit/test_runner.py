"""Offline unit tests for apitester.runner using a fake httpx-like client."""
import pytest

from apitester.models import RequestSpec
from apitester.runner import run_request

pytestmark = pytest.mark.unit


class FakeResponse:
    def __init__(self, status_code=200, json_data=None):
        self.status_code = status_code
        self._json = json_data

    def json(self):
        if self._json is None:
            raise ValueError("no json body")
        return self._json


class FakeClient:
    """Stand-in for httpx.Client that records calls and returns a fixed response."""

    def __init__(self, response: FakeResponse):
        self._response = response
        self.calls: list[dict] = []

    def request(self, method, url, **kwargs):
        self.calls.append({"method": method, "url": url, **kwargs})
        return self._response


def make_spec(**kwargs) -> RequestSpec:
    return RequestSpec.model_validate(kwargs)


def test_run_request_passes_captures_and_interpolates():
    client = FakeClient(FakeResponse(200, {"token": "abc"}))
    spec = make_spec(
        name="Auth",
        method="POST",
        url="{{base_url}}/auth",
        **{"assert": {"status": 200, "jsonpath": {"$.token": "abc"}}},
        capture={"token": "$.token"},
    )
    variables = {"base_url": "http://x"}

    result = run_request(client, spec, variables)

    assert result.passed
    assert result.status == 200
    # capture wrote the value back into the shared variables (chaining)
    assert variables["token"] == "abc"
    # placeholders were resolved before the call
    assert client.calls[0]["url"] == "http://x/auth"
    assert client.calls[0]["method"] == "POST"


def test_run_request_status_failure():
    client = FakeClient(FakeResponse(404, {"error": "nope"}))
    spec = make_spec(name="Get", url="{{base_url}}/a", **{"assert": {"status": 200}})

    result = run_request(client, spec, {"base_url": "http://x"})

    assert not result.passed
    assert result.status == 404


def test_run_request_handles_non_json_body():
    # A body that isn't JSON must not crash the runner.
    client = FakeClient(FakeResponse(200, None))
    spec = make_spec(name="Ping", url="{{u}}", **{"assert": {"status": 200}})

    result = run_request(client, spec, {"u": "http://x"})

    assert result.passed
    assert result.status == 200


def test_run_request_jsonpath_failure():
    client = FakeClient(FakeResponse(200, {"firstname": "Jim"}))
    spec = make_spec(
        name="Check",
        url="{{u}}",
        **{"assert": {"status": 200, "jsonpath": {"$.firstname": "Bob"}}},
    )

    result = run_request(client, spec, {"u": "http://x"})

    assert not result.passed
