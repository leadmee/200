"""Pydantic models describing the declarative collection format."""
from __future__ import annotations

from typing import Any, Optional

from pydantic import BaseModel, ConfigDict, Field


class Assertions(BaseModel):
    """Checks applied to a single response."""

    model_config = ConfigDict(populate_by_name=True)

    status: Optional[int] = None
    max_response_ms: Optional[int] = None
    # `schema` is aliased because BaseModel reserves the name internally.
    schema_path: Optional[str] = Field(default=None, alias="schema")
    jsonpath: dict[str, Any] = Field(default_factory=dict)


class RequestSpec(BaseModel):
    """A single request in a collection."""

    model_config = ConfigDict(populate_by_name=True)

    name: str
    method: str = "GET"
    url: str
    headers: dict[str, str] = Field(default_factory=dict)
    params: dict[str, Any] = Field(default_factory=dict)
    body: Any = None
    # `assert` is a Python keyword, so it is exposed via an alias.
    assertions: Assertions = Field(default_factory=Assertions, alias="assert")
    capture: dict[str, str] = Field(default_factory=dict)


class Collection(BaseModel):
    """An ordered list of requests executed as one run."""

    name: str = "Collection"
    requests: list[RequestSpec]
