"""Offline unit tests for apitester.loader (no network)."""
import pytest

from apitester.loader import interpolate, load_collection, load_environment

pytestmark = pytest.mark.unit


def test_interpolate_simple():
    assert interpolate("{{base_url}}/ping", {"base_url": "http://x"}) == "http://x/ping"


def test_interpolate_nested_dict_and_list():
    template = {
        "url": "{{base_url}}/booking",
        "body": {"user": "{{username}}"},
        "items": ["{{a}}", 2, True],
    }
    variables = {"base_url": "http://x", "username": "jim", "a": "A"}
    out = interpolate(template, variables)
    assert out["url"] == "http://x/booking"
    assert out["body"]["user"] == "jim"
    assert out["items"] == ["A", 2, True]


def test_interpolate_unknown_key_left_intact():
    # Unknown placeholders stay verbatim so failures are visible in the report.
    assert interpolate("{{missing}}", {}) == "{{missing}}"


@pytest.mark.parametrize("value", [111, True, None, 3.14])
def test_interpolate_non_string_leaf_unchanged(value):
    assert interpolate(value, {}) is value or interpolate(value, {}) == value


def test_load_environment_ok(tmp_path):
    env_file = tmp_path / "env.yaml"
    env_file.write_text(
        "environments:\n  prod:\n    base_url: http://x\n    username: admin\n",
        encoding="utf-8",
    )
    env = load_environment(env_file, "prod")
    assert env == {"base_url": "http://x", "username": "admin"}


def test_load_environment_missing_raises(tmp_path):
    env_file = tmp_path / "env.yaml"
    env_file.write_text("environments:\n  prod: {}\n", encoding="utf-8")
    with pytest.raises(KeyError):
        load_environment(env_file, "dev")


def test_load_collection_parses_aliases(tmp_path):
    collection_file = tmp_path / "c.yaml"
    collection_file.write_text(
        'name: X\n'
        'requests:\n'
        '  - name: r\n'
        '    method: POST\n'
        '    url: "{{base_url}}/a"\n'
        '    assert:\n'
        '      status: 200\n'
        '      schema: shared/schemas/auth_token.json\n'
        '    capture:\n'
        '      token: "$.token"\n',
        encoding="utf-8",
    )
    coll = load_collection(collection_file)
    assert coll.name == "X"
    req = coll.requests[0]
    assert req.method == "POST"
    assert req.assertions.status == 200
    assert req.assertions.schema_path == "shared/schemas/auth_token.json"
    assert req.capture == {"token": "$.token"}
