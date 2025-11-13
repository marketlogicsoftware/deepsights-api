"""
Unit tests for polling utilities.
"""

import pytest

from deepsights.utils._utils import (
    PollingFailedError,
    PollingTimeoutError,
    poll_for_completion,
)


def test_poll_for_completion_success(monkeypatch):
    calls = {"n": 0}

    def get_status(rid: str):
        calls["n"] += 1
        if calls["n"] < 3:
            return {"minion_job": {"status": "CREATED"}}
        return {"minion_job": {"status": "COMPLETED"}}

    def get_final(_rid: str):
        return "OK"

    # Speed up sleep
    monkeypatch.setattr("time.sleep", lambda s: None)
    result = poll_for_completion(
        get_status_func=get_status,
        resource_id="rid",
        timeout=5,
        polling_interval=0,
        get_final_result_func=get_final,
    )
    assert result == "OK"


def test_poll_for_completion_failure(monkeypatch):
    def get_status(_rid: str):
        return {"minion_job": {"status": "FAILED_ERROR", "error_message": "x"}}

    monkeypatch.setattr("time.sleep", lambda s: None)
    with pytest.raises(PollingFailedError):
        poll_for_completion(
            get_status_func=get_status,
            resource_id="rid",
            timeout=1,
            polling_interval=0,
        )


def test_poll_for_completion_timeout(monkeypatch):
    # Always pending, timeout=0 ensures immediate timeout
    def get_status(_rid: str):
        return {"minion_job": {"status": "CREATED"}}

    # Avoid any real sleep
    monkeypatch.setattr("time.sleep", lambda s: None)

    with pytest.raises(PollingTimeoutError):
        poll_for_completion(
            get_status_func=get_status,
            resource_id="rid",
            timeout=0,
            polling_interval=0,
        )
