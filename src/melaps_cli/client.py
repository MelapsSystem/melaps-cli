"""HTTP client for the Melaps API (v1, version 2026-06-22)."""

import time

import requests

from .errors import AuthError, MelapsError, NotFoundError, RateLimitError

API_VERSION = "2026-06-22"
DEFAULT_BASE_URL = "https://api.melaps.system/v1"


class Client:
    """Thin wrapper around the Melaps REST API.

    Authentication is a Bearer API key (``sk_live_...`` or ``sk_test_...``).
    Every mutating request carries an idempotency key, replayed for 24h by
    the API. Reads are rate limited at 600/min, job creation at 10/min.
    """

    def __init__(self, api_key, base_url=DEFAULT_BASE_URL, timeout=30):
        if not api_key:
            raise AuthError("no API key — run `melaps auth login` first")
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _headers(self, idempotency_key=None):
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Melaps-Version": API_VERSION,
            "Content-Type": "application/json",
        }
        if idempotency_key:
            headers["Idempotency-Key"] = idempotency_key
        return headers

    def request(self, method, path, json=None, idempotency_key=None):
        url = f"{self.base_url}{path}"
        for attempt in range(4):
            resp = self.session.request(
                method, url, json=json, headers=self._headers(idempotency_key),
                timeout=self.timeout,
            )
            if resp.status_code == 429:
                retry_after = int(resp.headers.get("Retry-After", "60"))
                if attempt < 3:
                    time.sleep(retry_after)
                    continue
                raise RateLimitError(retry_after)
            if resp.status_code == 401:
                raise AuthError("invalid API key")
            if resp.status_code == 404:
                raise NotFoundError(f"{method} {path} not found")
            if resp.status_code >= 400:
                raise MelapsError(f"{method} {path} failed: {resp.status_code} {resp.text[:200]}")
            return resp.json()
        raise MelapsError("request failed after retries")

    # -- jobs -------------------------------------------------------
    def submit_job(self, spec, idempotency_key=None):
        return self.request("POST", "/jobs", json=spec, idempotency_key=idempotency_key)

    def get_job(self, job_id):
        return self.request("GET", f"/jobs/{job_id}")

    def list_jobs(self, limit=20, cursor=None):
        params = f"?limit={limit}" + (f"&starting_after={cursor}" if cursor else "")
        return self.request("GET", f"/jobs{params}")

    def cancel_job(self, job_id):
        return self.request("POST", f"/jobs/{job_id}/cancel")

    def job_metrics(self, job_id):
        return self.request("GET", f"/jobs/{job_id}/metrics")

    # -- clusters, reservations, usage ------------------------------
    def list_clusters(self):
        return self.request("GET", "/clusters")

    def create_reservation(self, spec, idempotency_key=None):
        return self.request("POST", "/reservations", json=spec,
                            idempotency_key=idempotency_key)

    def usage(self, start, end):
        return self.request("GET", f"/usage?start={start}&end={end}")

    def status(self):
        return self.request("GET", "/status")
