"""
Unit test for deprecation warning in documents_search.
"""

import warnings
from typing import Any, cast

from deepsights.api.resource import APIResource
from deepsights.documentstore.resources.documents._search import documents_search


class _DummyAPI:
    def post(self, path, params=None, body=None, timeout=None, expected_statuscodes=None):
        # Return a minimal vector search-like structure
        return {
            "results": [
                {
                    "artifact_id": "doc1",
                    "result_parts": [
                        {"part_id": "p1", "score": 0.9},
                    ],
                }
            ]
        }


def test_documents_search_emits_deprecation_warning():
    resource = APIResource(api=cast(Any, _DummyAPI()))
    embedding = [0.0] * 1536
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        results = documents_search(
            resource=resource,
            query=None,
            query_embedding=embedding,
            min_score=0.0,
            max_results=1,
        )
        assert results
        assert any(issubclass(wi.category, DeprecationWarning) for wi in w)
