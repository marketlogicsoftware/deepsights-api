"""
Unit tests for userclient document_pages_load normalization and errors.
"""

import pytest

from deepsights.api.resource import APIResource
from deepsights.userclient.resources.documents.documents import document_pages_load


class _DummyAPI:
    def __init__(self, items):
        self._items = items

    def post(self, path, params=None, body=None, timeout=None, expected_statuscodes=None):
        return {"items": self._items}


def test_document_pages_load_normalizes_text():
    api = _DummyAPI(items=[{"id": "p1", "number": 2, "text": "Hello   world\n\n\nBye"}])
    res = APIResource(api=api)
    pages = document_pages_load(res, ["p1"])
    assert len(pages) == 1
    assert pages[0].id == "p1"
    assert pages[0].page_number == 2
    assert pages[0].text == "Hello world\n\nBye"


def test_document_pages_load_missing_pages_raises_404():
    api = _DummyAPI(items=[])
    res = APIResource(api=api)
    with pytest.raises(Exception) as exc:
        document_pages_load(res, ["missing"])
    # Should be HTTPError with a 404 status code
    assert hasattr(exc.value, "response")
    assert getattr(exc.value.response, "status_code", None) == 404
