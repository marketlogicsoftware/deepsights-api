"""
Validation tests for Content Store search functions.
"""

from typing import Any, cast

import pytest

from deepsights.api.resource import APIResource
from deepsights.contentstore.resources._search import (
    contentstore_hybrid_search,
    contentstore_text_search,
    contentstore_vector_search,
)


class _DummyAPI:
    def post(self, path, params=None, body=None, timeout=None, expected_statuscodes=None):
        raise AssertionError("Should not reach API when validation fails")


@pytest.mark.parametrize(
    "query,err_msg",
    [
        (None, "Query must be a string"),
        ("  ", "Query cannot be empty"),
        ("x" * 1001, "Query too long"),
    ],
)
def test_hybrid_search_query_validation(query, err_msg):
    res = APIResource(api=cast(Any, _DummyAPI()))
    with pytest.raises(ValueError) as exc:
        contentstore_hybrid_search(
            api=res.api,
            query=query,  # type: ignore[arg-type]
            item_type="NEWS",
            search_result=lambda i: i,
        )
    assert err_msg in str(exc.value)


@pytest.mark.parametrize(
    "args,err_msg",
    [
        ({"min_vector_score": -0.1}, "Minimum vector score"),
        ({"vector_fraction": 1.1}, "Vector fraction"),
        ({"vector_weight": -0.1}, "Vector weight"),
        ({"max_results": 251}, "Maximum results"),
        ({"recency_weight": 1.1}, "Recency weight"),
    ],
)
def test_hybrid_search_bounds_validation(args, err_msg):
    res = APIResource(api=cast(Any, _DummyAPI()))
    with pytest.raises(ValueError) as exc:
        contentstore_hybrid_search(
            api=res.api,
            query="ok",
            item_type="NEWS",
            search_result=lambda i: i,
            **args,
        )
    assert err_msg in str(exc.value)


@pytest.mark.parametrize(
    "embedding,err_msg",
    [
        (None, "Query embedding must be a list"),
        ([], "Query embedding cannot be empty"),
        ([0.0] * 10, "must be of length 1536"),
    ],
)
def test_vector_search_embedding_validation(embedding, err_msg):
    res = APIResource(api=cast(Any, _DummyAPI()))
    with pytest.raises(ValueError) as exc:
        contentstore_vector_search(
            api=res.api,
            query_embedding=embedding,  # type: ignore[arg-type]
            item_type="NEWS",
            search_result=lambda i: i,
        )
    assert err_msg in str(exc.value)


@pytest.mark.parametrize("max_results", [0, 101])
def test_text_search_max_results_validation(max_results):
    res = APIResource(api=cast(Any, _DummyAPI()))
    with pytest.raises(ValueError):
        contentstore_text_search(
            api=res.api,
            query="ok",
            item_type="NEWS",
            search_result=lambda i: i,
            max_results=max_results,
        )
