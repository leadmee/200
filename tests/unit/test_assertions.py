"""Offline unit tests for apitester.assertions (no network)."""
import pytest

from apitester import assertions as A

pytestmark = pytest.mark.unit


def test_check_status():
    assert A.check_status(200, 200).passed
    assert not A.check_status(200, 404).passed


def test_check_response_time():
    assert A.check_response_time(100, 50.0).passed
    assert A.check_response_time(100, 100.0).passed  # boundary is inclusive
    assert not A.check_response_time(100, 150.0).passed


def test_extract_jsonpath():
    assert A.extract_jsonpath("$.a.b", {"a": {"b": 5}}) == 5
    assert A.extract_jsonpath("$.missing", {}) is None


def test_check_jsonpath():
    assert A.check_jsonpath("$.a", "x", {"a": "x"}).passed
    assert not A.check_jsonpath("$.a", "y", {"a": "x"}).passed


def test_validate_schema_pass_and_fail(tmp_path):
    schema = tmp_path / "s.json"
    schema.write_text(
        '{"type": "object", "required": ["token"],'
        ' "properties": {"token": {"type": "string"}}}',
        encoding="utf-8",
    )
    assert A.validate_schema(schema, {"token": "abc"}).passed
    failing = A.validate_schema(schema, {})  # missing required "token"
    assert not failing.passed
    assert "token" in failing.detail


def test_validate_schema_missing_file(tmp_path):
    result = A.validate_schema(tmp_path / "nope.json", {})
    assert not result.passed
