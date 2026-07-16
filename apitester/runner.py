"""Execute a collection: run each request, apply assertions, capture vars."""
from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Optional

import httpx

from apitester import assertions as checks
from apitester.assertions import CheckResult
from apitester.loader import interpolate
from apitester.models import Collection, RequestSpec


@dataclass
class RequestResult:
    name: str
    method: str
    url: str
    status: Optional[int]
    elapsed_ms: float
    checks: list[CheckResult] = field(default_factory=list)
    error: Optional[str] = None

    @property
    def passed(self) -> bool:
        return self.error is None and all(c.passed for c in self.checks)


def run_request(client: httpx.Client, spec: RequestSpec, variables: dict[str, Any]) -> RequestResult:
    method = str(interpolate(spec.method, variables)).upper()
    url = interpolate(spec.url, variables)
    headers = interpolate(spec.headers, variables)
    params = interpolate(spec.params, variables)
    body = interpolate(spec.body, variables)

    try:
        start = time.perf_counter()
        kwargs: dict[str, Any] = {"headers": headers, "params": params}
        if body is not None:
            kwargs["json"] = body
        response = client.request(method, url, **kwargs)
        elapsed_ms = (time.perf_counter() - start) * 1000
    except httpx.HTTPError as exc:
        return RequestResult(spec.name, method, url, None, 0.0, error=str(exc))

    try:
        parsed = response.json()
    except ValueError:
        parsed = None

    results: list[CheckResult] = []
    a = spec.assertions
    if a.status is not None:
        results.append(checks.check_status(a.status, response.status_code))
    if a.max_response_ms is not None:
        results.append(checks.check_response_time(a.max_response_ms, elapsed_ms))
    if a.schema_path:
        results.append(checks.validate_schema(a.schema_path, parsed))
    for expr, expected in (a.jsonpath or {}).items():
        results.append(checks.check_jsonpath(expr, expected, parsed))

    # Capture values for use in subsequent requests (chaining).
    if parsed is not None:
        for var_name, expr in spec.capture.items():
            value = checks.extract_jsonpath(expr, parsed)
            if value is not None:
                variables[var_name] = value

    return RequestResult(spec.name, method, url, response.status_code, elapsed_ms, results)


def run_collection(
    collection: Collection,
    variables: dict[str, Any],
    timeout: float = 30.0,
) -> list[RequestResult]:
    """Run every request in order, mutating ``variables`` with captures."""
    results: list[RequestResult] = []
    with httpx.Client(timeout=timeout) as client:
        for spec in collection.requests:
            results.append(run_request(client, spec, variables))
    return results
