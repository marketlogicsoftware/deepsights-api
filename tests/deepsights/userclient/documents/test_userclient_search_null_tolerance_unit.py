"""
Unit tests for null-tolerant parsing of userclient search responses (no network).

A degraded backend may return HTTP 200 with "context": null or
"search_results": null; both must be treated as an empty result set.
"""

import pytest

from deepsights.api.resource import APIResource
from deepsights.userclient.resources.documents.documents import hybrid_search, topic_search


class _DummyAPI:
    def __init__(self, response):
        self._response = response

    def post(self, path, params=None, body=None, timeout=None, expected_statuscodes=None):
        return self._response


_ARTIFACT = {
    "artifact_id": "art-1",
    "artifact_title": "Title",
    "artifact_summary": "Summary",
    "artifact_source": "Source",
    "artifact_content_type": "standalone_document",
    "artifact_publication_date": "2024-01-02T03:04:05Z",
}

_HYBRID_RESULT = {
    **_ARTIFACT,
    "page_references": [{"id": "page-1", "external_id": None, "number": 1, "title": "P1", "text": "Text"}],
}

_TOPIC_RESULT = {
    **_ARTIFACT,
    "page_references": [
        {
            "id": "page-1",
            "external_id": None,
            "number": 1,
            "title": "P1",
            "text": "Text",
            "relevance_class": "HIGH",
            "relevance_assessment": "Good match",
        }
    ],
    "relevance_class": "HIGH",
    "relevance_assessment": "Good match",
}

_NULL_RESPONSES = [
    {"context": None},
    {"context": {"search_results": None}},
    {"context": {}},
    {},
]
_NULL_IDS = ["context-null", "search-results-null", "context-empty", "no-context-key"]


@pytest.mark.parametrize("response", _NULL_RESPONSES, ids=_NULL_IDS)
def test_hybrid_search_null_response_returns_empty(response):
    resource = APIResource(api=_DummyAPI(response))
    assert hybrid_search(resource, "query") == []


@pytest.mark.parametrize("response", _NULL_RESPONSES, ids=_NULL_IDS)
def test_topic_search_null_response_returns_empty(response):
    resource = APIResource(api=_DummyAPI(response))
    assert topic_search(resource, "query") == []


def test_hybrid_search_parses_non_empty_payload():
    resource = APIResource(api=_DummyAPI({"context": {"search_results": [_HYBRID_RESULT]}}))
    results = hybrid_search(resource, "query")
    assert len(results) == 1
    assert results[0].artifact_id == "art-1"
    assert results[0].page_references[0].id == "page-1"


def test_topic_search_parses_non_empty_payload_and_skips_empty_entries():
    resource = APIResource(api=_DummyAPI({"context": {"search_results": [_TOPIC_RESULT, {}, None]}}))
    results = topic_search(resource, "query")
    assert len(results) == 1
    assert results[0].artifact_id == "art-1"
    assert results[0].relevance_class == "HIGH"
