"""Declarative HTTP API tester (Postman/Insomnia-lite).

Describe collections of requests in YAML, run them, and assert on status
codes, response time, JSON Schema and JSONPath values.
"""

__all__ = ["models", "loader", "assertions", "runner", "reporter", "cli"]
