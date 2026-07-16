"""Thin client for the restful-booker API, shared by the pytest suite.

Every call is wrapped in an ``allure.step`` and attaches the request/response
bodies so the Allure report shows full context for each action.
"""
from __future__ import annotations

from typing import Any, Optional

import allure
import requests


class BookingAPI:
    def __init__(self, base_url: str, timeout: float = 30.0) -> None:
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

    # -- internal helpers ---------------------------------------------------
    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    @staticmethod
    def _attach(response: requests.Response) -> None:
        try:
            req = response.request
            allure.attach(
                (req.body or b"") if isinstance(req.body, (bytes, bytearray)) else str(req.body or ""),
                name=f"{req.method} {req.url}",
                attachment_type=allure.attachment_type.TEXT,
            )
            allure.attach(
                response.text,
                name=f"Response {response.status_code}",
                attachment_type=allure.attachment_type.TEXT,
            )
        except Exception:  # pragma: no cover - reporting must never break a test
            pass

    @staticmethod
    def _auth_headers(token: Optional[str]) -> dict[str, str]:
        return {"Cookie": f"token={token}"} if token is not None else {}

    # -- endpoints ----------------------------------------------------------
    def ping(self) -> requests.Response:
        with allure.step("GET /ping (health check)"):
            resp = self.session.get(self._url("/ping"), timeout=self.timeout)
            self._attach(resp)
            return resp

    def create_auth_token(self, username: str, password: str) -> requests.Response:
        with allure.step("POST /auth"):
            resp = self.session.post(
                self._url("/auth"),
                json={"username": username, "password": password},
                timeout=self.timeout,
            )
            self._attach(resp)
            return resp

    def create_booking(self, payload: dict[str, Any]) -> requests.Response:
        with allure.step("POST /booking"):
            resp = self.session.post(self._url("/booking"), json=payload, timeout=self.timeout)
            self._attach(resp)
            return resp

    def get_booking(self, booking_id: int) -> requests.Response:
        with allure.step(f"GET /booking/{booking_id}"):
            resp = self.session.get(self._url(f"/booking/{booking_id}"), timeout=self.timeout)
            self._attach(resp)
            return resp

    def get_booking_ids(self, params: Optional[dict[str, Any]] = None) -> requests.Response:
        with allure.step("GET /booking"):
            resp = self.session.get(self._url("/booking"), params=params, timeout=self.timeout)
            self._attach(resp)
            return resp

    def update_booking(
        self, booking_id: int, payload: dict[str, Any], token: Optional[str]
    ) -> requests.Response:
        with allure.step(f"PUT /booking/{booking_id}"):
            resp = self.session.put(
                self._url(f"/booking/{booking_id}"),
                json=payload,
                headers=self._auth_headers(token),
                timeout=self.timeout,
            )
            self._attach(resp)
            return resp

    def partial_update_booking(
        self, booking_id: int, payload: dict[str, Any], token: Optional[str]
    ) -> requests.Response:
        with allure.step(f"PATCH /booking/{booking_id}"):
            resp = self.session.patch(
                self._url(f"/booking/{booking_id}"),
                json=payload,
                headers=self._auth_headers(token),
                timeout=self.timeout,
            )
            self._attach(resp)
            return resp

    def delete_booking(self, booking_id: int, token: Optional[str]) -> requests.Response:
        with allure.step(f"DELETE /booking/{booking_id}"):
            resp = self.session.delete(
                self._url(f"/booking/{booking_id}"),
                headers=self._auth_headers(token),
                timeout=self.timeout,
            )
            self._attach(resp)
            return resp
