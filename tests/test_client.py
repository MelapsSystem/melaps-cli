from unittest.mock import Mock

import pytest

from melaps_cli.client import Client
from melaps_cli.errors import AuthError, NotFoundError


def _client(status=200, payload=None, headers=None):
    c = Client("sk_test_123")
    resp = Mock()
    resp.status_code = status
    resp.headers = headers or {}
    resp.json.return_value = payload or {}
    resp.text = ""
    c.session.request = Mock(return_value=resp)
    return c


def test_missing_key_raises():
    with pytest.raises(AuthError):
        Client("")


def test_get_job_returns_payload():
    c = _client(payload={"id": "job-01k4", "status": "RUNNING"})
    assert c.get_job("job-01k4")["status"] == "RUNNING"


def test_404_becomes_not_found():
    c = _client(status=404)
    with pytest.raises(NotFoundError):
        c.get_job("job-nope")


def test_submit_sends_idempotency_key():
    c = _client(payload={"id": "job-01k5", "status": "QUEUED"})
    c.submit_job({"image": "pytorch:2.5"}, idempotency_key="key-1")
    _, kwargs = c.session.request.call_args
    assert kwargs["headers"]["Idempotency-Key"] == "key-1"
    assert kwargs["headers"]["Melaps-Version"] == "2026-06-22"
