# Copyright 2024 Market Logic Software AG. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This module contains the tests for the secondary search functionality of the DeepSights ContentStore.
"""

import re
import json
import shlex
import pytest
import deepsights
from deepsights.contentstore.secondary import (
    _secondary_text_search,
    _secondary_vector_search,
)

# get the test data from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    data = json.load(f)
    test_embedding = data["embedding"]
    test_query = data["question"]


def test_secondary_text_search():
    """
    Test case for performing a text search on secondary content.

    This function tests the `_secondary_text_search` method of the `ContentStore` class.
    It verifies that the search results contain the expected number of items,
    and that each result has a valid ID and source. It also checks that the rank
    of each result is greater than the rank of the previous result.

    Note: This test assumes the existence of a `test_query` variable.
    """
    results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=5,
    )

    assert len(results) == 5
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.source is not None

        if ix > 0:
            assert result.rank > results[ix - 1].rank


def test_secondary_text_search_with_recency_low():
    """
    Test the secondary text search function with a low recency weight.

    This test verifies that the secondary text search function returns results
    when the recency weight is set to a low value. It checks that the
    returned results have valid IDs, ranks, score ranks, and age ranks,
    and that the final rank is identical to the score rank.

    Note: This test assumes the existence of a `test_query` variable.
    """

    results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=10,
        recency_weight=0.00001,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1
        assert result.score_rank == result.rank
        assert result.age_rank is not None


def test_secondary_text_search_with_recency_high():
    """
    Test the secondary text search function with a high recency weight.

    This test verifies that the secondary text search function returns results
    when the recency weight is set to a high value. It checks that the
    returned results have valid IDs, ranks, score ranks, and age ranks,
    and that the final rank is identical to the age rank.

    Note: This test assumes the existence of a `test_query` variable.
    """
    results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=10,
        recency_weight=0.99999,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1
        assert result.score_rank is not None
        assert result.age_rank == result.rank


def test_secondary_vector_search():
    """
    Test the secondary vector search function.

    This function tests the _secondary_vector_search function by calling it with a test embedding
    and asserting that the returned results have the expected length and properties.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = _secondary_vector_search(
        deepsights.ContentStore(),
        test_embedding,
        max_results=5,
    )

    assert len(results) == 5
    for ix, result in enumerate(results):
        assert result.id is not None

        if ix > 0:
            assert result.rank > results[ix - 1].rank


def test_secondary_vector_search_with_recency_low():
    """
    Test the secondary vector search with a low recency weight.

    This test function performs a secondary vector search using a low recency weight
    and asserts that the results meet certain criteria especially
    that the score rank is identical to the final rank.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = _secondary_vector_search(
        deepsights.ContentStore(),
        test_embedding,
        max_results=10,
        recency_weight=0.00001,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1
        assert result.score_rank == result.rank
        assert result.age_rank is not None


def test_secondary_vector_search_with_recency_high():
    """
    Test the secondary vector search with high recency weight.

    This test function performs a secondary vector search using a high recency weight
    and asserts that the returned results meet certain criteria, especially
    that the age rank is identical to the final rank.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = _secondary_vector_search(
        deepsights.ContentStore(),
        test_embedding,
        max_results=10,
        recency_weight=0.99999,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1
        assert result.score_rank is not None
        assert result.age_rank == result.rank


def test_secondary_hybrid_search_fail():
    """
    Test case to verify that a ValueError is raised when performing a hybrid secondary search
    with no query or query embedding.

    Raises:
        ValueError: If the `deepsights.secondary_search` function does not raise a ValueError.
    """
    with pytest.raises(ValueError):
        deepsights.secondary_search(
            deepsights.ContentStore(),
            max_results=5,
        )


def test_secondary_hybrid_search_only_vector():
    """
    Test the hybrid secondary search function with only query vector input.

    This test case verifies that the hybrid secondary search function returns the same results as the vector search function
    when only the query vector is provided as input.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        max_results=5,
    )

    vector_results = _secondary_vector_search(
        deepsights.ContentStore(),
        test_embedding,
        max_results=5,
    )

    assert len(hybrid_results) == 5
    for ix, hybrid_result in enumerate(hybrid_results):
        assert hybrid_result == vector_results[ix]


def test_secondary_hybrid_search_only_text():
    """
    Test case for performing hybrid search with only text query.

    This test case verifies that the hybrid search function returns the same results
    when performing a search using only the text query parameter, as a plain
    text query does.

    Note: This test assumes the existence of a `test_query` variable.
    """
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=5,
    )

    text_results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=5,
    )

    assert len(hybrid_results) == 5
    for ix, hybrid_result in enumerate(hybrid_results):
        assert hybrid_result == text_results[ix]


def test_secondary_hybrid_search():
    """
    Test case for hybrid secondary search.

    This function tests the hybrid secondary search functionality by performing a search using both
    query embeddings and text queries. It compares the results from the hybrid search with the
    results from vector search and text search, ensuring that all the results from the hybrid
    search are present in the results from vector search and text search.

    Note: This test assumes the existence of `test_embedding` and `test_query` variables.
    """
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        query=test_query,
        max_results=10,
    )

    vector_results = _secondary_vector_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        max_results=10,
    )

    text_results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=10,
    )

    assert len(hybrid_results) == 10

    hybrid_ids = [result.id for result in hybrid_results]

    contrib_ids = [result.id for result in vector_results]
    contrib_ids += [result.id for result in text_results]

    assert all([result in contrib_ids for result in hybrid_ids])


def test_secondary_hybrid_search_with_vector_high():
    """
    Test case for performing hybrid search with a high vector weight, checking
    that the final ranking is that same as the vector ranking.

    Note: This test assumes the existence of `test_embedding` and `test_query` variables.
    """
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        query=test_query,
        max_results=10,
        vector_weight=0.99999,
    )

    vector_results = _secondary_vector_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        max_results=10,
    )

    assert len(hybrid_results) == 10
    for ix, result in enumerate(hybrid_results):
        assert result.id == vector_results[ix].id


def test_secondary_hybrid_search_with_vector_low():
    """
    Test case for performing hybrid search with a low vector weight, checking
    that the final ranking is that same as the text ranking.

    Note: This test assumes the existence of `test_embedding` and `test_query` variables.
    """
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        query=test_query,
        max_results=10,
        vector_weight=0.00001,
    )

    text_results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=10,
    )

    assert len(hybrid_results) == 10
    for ix, result in enumerate(hybrid_results):
        assert result.id == text_results[ix].id


def test_secondary_text_search_with_title_promotion():
    """
    Test case for performing a secondary text search with title promotion.

    This test case verifies that the hybrid search function returns the expected results
    when searching for secondary articles based on a query with title promotion enabled.
    """
    query = "gen x digital buyers"

    # first find top 10 results without title promotion and hard recency weight
    hybrid_results_no_promotion = deepsights.secondary_search(
        deepsights.ContentStore(),
        query=query,
        max_results=50,
        promote_exact_match=False,
        recency_weight=0.99,
    )

    # helper to find a result that matches the query exactly
    def matches(query, result):
        return all(
            [
                re.search(
                    rf"(?:\b|\s|^){re.escape(term)}(?:\b|\s|$|\W)",
                    result.title,
                    re.IGNORECASE,
                )
                for term in shlex.split(query)
            ]
        )
    # must not match top result
    assert not matches(query, hybrid_results_no_promotion[0])

    # find first result with index > 1 with that matches the query exactly
    ix = 0
    for ix, result in enumerate(hybrid_results_no_promotion[1:], 1):
        if matches(query, result):
            break
   
    assert ix > 0
    assert ix < len(hybrid_results_no_promotion)-1

    # now retrieve with title promotion
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query=query,
        max_results=50,
        promote_exact_match=True,
        recency_weight=0.99,
    )

    assert hybrid_results[0].id == hybrid_results_no_promotion[ix].id
    assert matches(query, hybrid_results[0])
