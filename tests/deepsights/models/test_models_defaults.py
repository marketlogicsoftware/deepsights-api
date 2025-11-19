# Copyright 2024-2025 Market Logic Software AG.

"""
Unit tests for model defaults and defensive parsing.
"""

from typing import Any, cast

from deepsights.contentstore.resources._model import ContentStoreSearchResult
from deepsights.documentstore.resources.documents._model import Document
from deepsights.userclient.resources.answersV2._model import AnswerV2


def test_document_defensive_parsing_missing_nested_fields():
    # Should not raise when origin/publication_data are missing
    doc = Document(id="doc-1", title="Test", status="AVAILABLE", content_type="doc", summary=None, external_metadata={})
    assert doc.creation_date is None
    assert doc.publication_date is None
    # page_ids now default to empty list
    assert isinstance(doc.page_ids, list)
    assert doc.page_ids == []


def test_list_default_factories_not_shared_between_instances():
    a = AnswerV2(
        id="a",
        permission_validation="GRANTED",
        status="COMPLETED",
        question="Q1",
    )
    b = AnswerV2(
        id="b",
        permission_validation="GRANTED",
        status="COMPLETED",
        question="Q2",
    )

    assert a.document_sources == [] and b.document_sources == []
    a.document_sources.append(cast(Any, object()))
    assert len(a.document_sources) == 1
    assert b.document_sources == []  # not shared


def test_contentstore_paragraphs_default_list():
    cs = ContentStoreSearchResult(id="x", title="t", description="d", url="u")
    assert isinstance(cs.paragraphs, list)
    assert cs.paragraphs == []
