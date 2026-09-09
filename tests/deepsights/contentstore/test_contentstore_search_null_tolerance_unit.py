"""
Unit tests for null-tolerant parsing of Content Store search responses (no network).

A degraded backend may return HTTP 200 with "items": null (or no "items" key);
this must be treated as an empty result set.
"""

from typing import Any, cast

import pytest

from deepsights.contentstore.resources._model import ContentStoreSearchResult
from deepsights.contentstore.resources._search import (
    contentstore_hybrid_search,
    contentstore_text_search,
    contentstore_vector_search,
)


class _DummyAPI:
    def __init__(self, response):
        self._response = response

    def post(self, path, params=None, body=None, timeout=None, expected_statuscodes=None):
        return self._response


_ITEM = {
    "id": "item-1",
    "title": "Title",
    "description": "Description",
    "url": "https://example.com",
    "language": "en",
    "publication_date": "2024-01-02T03:04:05Z",
    "source": "Source",
    "source_id": "src-1",
}

_NULL_RESPONSES = [{"items": None}, {}]
_NULL_IDS = ["items-null", "no-items-key"]


def _search_result(i: Any) -> ContentStoreSearchResult:
    return ContentStoreSearchResult(**i)


@pytest.mark.parametrize("response", _NULL_RESPONSES, ids=_NULL_IDS)
def test_hybrid_search_null_response_returns_empty(response):
    api = cast(Any, _DummyAPI(response))
    assert contentstore_hybrid_search(api, "query", item_type="NEWS", search_result=_search_result) == []


@pytest.mark.parametrize("response", _NULL_RESPONSES, ids=_NULL_IDS)
def test_text_search_null_response_returns_empty(response):
    api = cast(Any, _DummyAPI(response))
    assert contentstore_text_search(api, "query", item_type="NEWS", search_result=_search_result) == []


@pytest.mark.parametrize("response", _NULL_RESPONSES, ids=_NULL_IDS)
def test_vector_search_null_response_returns_empty(response):
    api = cast(Any, _DummyAPI(response))
    assert contentstore_vector_search(api, [0.0] * 1536, item_type="NEWS", search_result=_search_result) == []


def test_hybrid_search_parses_non_empty_payload_and_records_rank():
    api = cast(Any, _DummyAPI({"items": [_ITEM, {**_ITEM, "id": "item-2"}]}))
    results = contentstore_hybrid_search(api, "query", item_type="NEWS", search_result=_search_result)
    assert [r.id for r in results] == ["item-1", "item-2"]
    assert [r.rank for r in results] == [1, 2]


def test_text_search_parses_non_empty_payload_and_records_rank():
    api = cast(Any, _DummyAPI({"items": [_ITEM]}))
    results = contentstore_text_search(api, "query", item_type="NEWS", search_result=_search_result)
    assert len(results) == 1
    assert results[0].id == "item-1"
    assert results[0].rank == 1


def test_vector_search_parses_non_empty_payload():
    api = cast(Any, _DummyAPI({"items": [_ITEM]}))
    results = contentstore_vector_search(api, [0.0] * 1536, item_type="NEWS", search_result=_search_result)
    assert len(results) == 1
    assert results[0].id == "item-1"
