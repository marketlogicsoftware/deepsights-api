"""
Unit tests for the publication date fields on Document (no network).

artifact-service exposes several publication dates on `publication_data`. The historical
`publication_date` is deprecated there and is left unset whenever the date came from AI
extraction, so `effective_publication_date` is the field callers should read.
"""

from datetime import datetime, timezone

from deepsights.documentstore.resources.documents._cache import set_document
from deepsights.documentstore.resources.documents._model import Document, DocumentSearchResult


def _document(**overrides):
    """Build a minimally valid Document, overriding whatever the test cares about."""
    payload = {
        "id": "doc-1",
        "title": "Test",
        "status": "COMPLETED",
        "content_type": "standalone_document",
        "summary": None,
    }
    payload.update(overrides)
    return Document(**payload)


def test_document_exposes_effective_publication_date():
    doc = _document(
        publication_data={
            "publication_date": None,
            "effective_publication_date": "2026-02-02T00:00:00Z",
        }
    )

    assert doc.effective_publication_date == datetime(2026, 2, 2, tzinfo=timezone.utc)


def test_document_exposes_externally_and_ai_provided_publication_dates():
    doc = _document(
        publication_data={
            "externally_provided_publication_date": "2025-05-05T00:00:00Z",
            "ai_provided_publication_date": "2024-04-04T00:00:00Z",
        }
    )

    assert doc.externally_provided_publication_date == datetime(2025, 5, 5, tzinfo=timezone.utc)
    assert doc.ai_provided_publication_date == datetime(2024, 4, 4, tzinfo=timezone.utc)


def test_effective_publication_date_is_set_when_deprecated_field_is_null():
    """The production case: AI-extracted dates never populate the deprecated field."""
    doc = _document(
        publication_data={
            "publication_date": None,
            "externally_provided_publication_date": None,
            "ai_provided_publication_date": "2026-02-02T00:00:00Z",
            "effective_publication_date": "2026-02-02T00:00:00Z",
        }
    )

    assert doc.publication_date is None
    assert doc.effective_publication_date == datetime(2026, 2, 2, tzinfo=timezone.utc)


def test_deprecated_publication_date_still_maps_from_publication_data():
    """Existing behaviour must not change for callers still reading publication_date."""
    doc = _document(publication_data={"publication_date": "2023-03-03T00:00:00Z"})

    assert doc.publication_date == datetime(2023, 3, 3, tzinfo=timezone.utc)


def test_publication_dates_default_to_none_without_publication_data():
    doc = _document(external_metadata={})

    assert doc.publication_date is None
    assert doc.effective_publication_date is None
    assert doc.externally_provided_publication_date is None
    assert doc.ai_provided_publication_date is None


def test_external_metadata_exposes_external_creation_date():
    """Third rung of the effective-date chain"""
    doc = _document(external_metadata={"external_creation_date": "2022-06-06T00:00:00Z"})

    assert doc.external_metadata is not None
    assert doc.external_metadata.external_creation_date == datetime(2022, 6, 6, tzinfo=timezone.utc)


def test_document_search_result_exposes_effective_publication_date():
    doc = _document(
        id="doc-search-1",
        publication_data={"effective_publication_date": "2026-07-07T00:00:00Z"},
    )
    set_document(doc.id, doc)

    result = DocumentSearchResult(id="doc-search-1")

    assert result.effective_publication_date == datetime(2026, 7, 7, tzinfo=timezone.utc)


def test_document_search_result_effective_publication_date_is_none_when_uncached():
    result = DocumentSearchResult(id="not-in-cache")

    assert result.effective_publication_date is None


class _DummyAPI:
    def __init__(self, response):
        self._response = response
        self.calls = []

    def post(self, path, params=None, body=None, timeout=None, expected_statuscodes=None):
        self.calls.append((path, body))
        return self._response


class _DummyResource:
    def __init__(self, response):
        self.api = _DummyAPI(response)


_SEARCH_RESPONSE = {
    "total_items": 1,
    "items": [
        {
            "id": "art-1",
            "title": "Report One",
            "status": "COMPLETED",
            "content_type": "standalone_document",
            "summary": "a summary",
            "type": "ORIGINAL_PDF",
            "origin": {"creation_time": "2026-08-18T11:24:55Z"},
            "publication_data": {
                "publication_date": None,
                "externally_provided_publication_date": None,
                "ai_provided_publication_date": "2026-02-02T00:00:00Z",
                "effective_publication_date": "2026-02-02T00:00:00Z",
            },
        }
    ],
}


def test_documentstore_documents_list_propagates_effective_publication_date():
    """Guards the mapping through model_validate, which is how the real list path builds Documents."""
    from deepsights.documentstore.resources.documents._list import documents_list

    total, documents = documents_list(_DummyResource(_SEARCH_RESPONSE))

    assert total == 1
    assert documents[0].publication_date is None
    assert documents[0].effective_publication_date == datetime(2026, 2, 2, tzinfo=timezone.utc)
    assert documents[0].ai_provided_publication_date == datetime(2026, 2, 2, tzinfo=timezone.utc)


def test_userclient_documents_list_propagates_effective_publication_date():
    from deepsights.userclient.resources.documents.documents import documents_list

    total, documents = documents_list(_DummyResource(_SEARCH_RESPONSE))

    assert total == 1
    assert documents[0].effective_publication_date == datetime(2026, 2, 2, tzinfo=timezone.utc)
