"""
Unit tests for AnswersV2 and Reports resources (no network).
"""

from typing import Any, cast

import pytest
from ratelimit import RateLimitException

from deepsights.exceptions import RateLimitError
from deepsights.userclient.resources.answersV2.answerV2 import AnswerV2Resource
from deepsights.userclient.resources.reports.report import ReportResource


class _DummyAPIAnswers:
    def __init__(self):
        self.calls = 0

    def post(self, path, params=None, body=None, timeout=None, expected_statuscodes=None):
        raise RateLimitException("Rate limit exceeded", 60)

    def get(self, path, params=None, timeout=None, expected_statuscodes=None):
        # Emulate polling then final response
        self.calls += 1
        if self.calls < 2:
            return {"answer_v2": {"minion_job": {"status": "CREATED"}}}
        return {
            "permission_validation_result": "GRANTED",
            "answer_v2": {
                "minion_job": {"id": "rid", "status": "COMPLETED"},
                "context": {
                    "input": "Q",
                    "summary": {"answer": "A", "watchouts": "W"},
                    "avs_results": [],
                    "srs_results": [],
                    "sns_results": [],
                    "avs_suggestions": [],
                    "srs_suggestions": [],
                    "sns_suggestions": [],
                },
            },
        }


class _DummyAPIAnswersRestricted:
    def get(self, path, params=None, timeout=None, expected_statuscodes=None):
        return {
            "permission_validation_result": "RESTRICTED",
            "restricted_answer_v2": {"answer_v2_id": "rid", "input": "Q"},
        }


def test_answers_create_rate_limit_translated():
    res = AnswerV2Resource(cast(Any, _DummyAPIAnswers()))
    with pytest.raises(RateLimitError):
        res.create("Q")


def test_answers_create_and_wait_rate_limit_translated(monkeypatch):
    res = AnswerV2Resource(cast(Any, _DummyAPIAnswers()))

    def raiser(_q):
        raise RateLimitException("Rate limit exceeded", 60)

    monkeypatch.setattr(res, "create", raiser)
    with pytest.raises(RateLimitError):
        res.create_and_wait("Q")


def test_answers_wait_for_answer_success(monkeypatch):
    res = AnswerV2Resource(cast(Any, _DummyAPIAnswers()))
    monkeypatch.setattr("time.sleep", lambda s: None)
    ans = res.wait_for_answer("rid", timeout=1)
    assert ans.status == "COMPLETED"
    assert ans.question == "Q"
    assert ans.answer == "A"


def test_answers_get_restricted():
    res = AnswerV2Resource(cast(Any, _DummyAPIAnswersRestricted()))
    ans = res.get("rid")
    assert ans.permission_validation in ("RESTRICTED",)
    assert ans.status == "n/a"
    assert ans.question == "Q"


class _DummyAPIReports:
    def __init__(self):
        self.calls = 0

    def post(self, path, params=None, body=None, timeout=None, expected_statuscodes=None):
        raise RateLimitException("Rate limit exceeded", 60)

    def get(self, path, params=None, timeout=None, expected_statuscodes=None):
        self.calls += 1
        if self.calls < 2:
            return {"desk_research": {"minion_job": {"status": "CREATED"}}}
        return {
            "permission_validation_result": "GRANTED",
            "desk_research": {
                "minion_job": {"id": "rid", "status": "COMPLETED"},
                "context": {
                    "input": "Q",
                    "topic": "T",
                    "summary": "S",
                    "artifact_vector_search_results": [],
                    "scs_report_search_results": [],
                    "scs_news_search_results": [],
                },
            },
        }


class _DummyAPIReportsRestricted:
    def get(self, path, params=None, timeout=None, expected_statuscodes=None):
        return {
            "permission_validation_result": "RESTRICTED",
            "restricted_desk_research": {"desk_research_id": "rid", "input": "Q"},
        }


class _DummyAPIReportsDeleted:
    def get(self, path, params=None, timeout=None, expected_statuscodes=None):
        return {"permission_validation_result": "DELETED_CONTENT"}


def test_reports_create_rate_limit_translated():
    res = ReportResource(cast(Any, _DummyAPIReports()))
    with pytest.raises(RateLimitError):
        res.create("Q")


def test_reports_wait_for_report_success(monkeypatch):
    res = ReportResource(cast(Any, _DummyAPIReports()))
    monkeypatch.setattr("time.sleep", lambda s: None)
    rep = res.wait_for_report("rid", timeout=1)
    assert rep.status == "COMPLETED"
    assert rep.question == "Q"
    assert rep.topic == "T"
    assert rep.summary == "S"


def test_reports_get_restricted():
    res = ReportResource(cast(Any, _DummyAPIReportsRestricted()))
    rep = res.get("rid")
    assert rep.permission_validation in ("RESTRICTED",)
    assert rep.status == "n/a"
    assert rep.question == "Q"


def test_reports_get_deleted_returns_none():
    res = ReportResource(_DummyAPIReportsDeleted())
    assert res.get("rid") is None
