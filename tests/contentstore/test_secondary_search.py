# Copyright 2024-2025 Market Logic Software AG. All Rights Reserved.
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

from datetime import datetime, timedelta, timezone

from tests.helpers.common import equal_results
from tests.helpers.validation import (
    assert_ascending_publication_dates,
    assert_ascending_ranks,
    assert_date_range_filter,
    assert_descending_publication_dates,
    assert_language_filter,
    assert_ranked_results,
    assert_valid_contentstore_result,
)


def test_secondary_text_search(ds_client, test_data):
    """
    Test case for performing a text search on secondary content.

    This function tests the `text_search` method of the `ContentStore` class.
    It verifies that the search results contain the expected number of items,
    and that each result has a valid ID and source. It also checks that the rank
    of each result is greater than the rank of the previous result.
    """
    results = ds_client.contentstore.secondary.text_search(
        query=test_data["question"],
        max_results=5,
    )

    assert len(results) == 5
    for result in results:
        assert_valid_contentstore_result(result)
    assert_ascending_ranks(results)


def test_secondary_text_empty_search(ds_client):
    """ """
    results = ds_client.contentstore.secondary.text_search(
        query="",
        max_results=50,
    )

    assert len(results) == 50
    for result in results:
        assert_valid_contentstore_result(result)
    assert_descending_publication_dates(results)


def test_secondary_download(ds_client):
    """ """
    results = ds_client.contentstore.secondary.text_search(
        query="",
        max_results=1,
        search_to_timestamp=datetime.now(timezone.utc) - timedelta(days=100),
    )

    content = ds_client.contentstore.secondary.download(results[-1].id)
    assert len(content) > 0


def test_secondary_text_search_offset(ds_client, test_data):
    """
    Test the secondary text search function with an offset.
    """
    results = ds_client.contentstore.secondary.text_search(
        query=test_data["question"],
        max_results=5,
    )
    offset_results = ds_client.contentstore.secondary.text_search(
        query=test_data["question"],
        max_results=4,
        offset=1,
    )
    for ix, result in enumerate(offset_results):
        assert equal_results(result, results[ix + 1])


def test_secondary_text_search_language(ds_client, test_data):
    """
    Test the secondary text search function with a language filter.
    """
    results = ds_client.contentstore.secondary.text_search(
        query=test_data["question"],
        max_results=5,
        languages=["en"],
    )
    assert len(results) == 5
    assert_language_filter(results, ["en"])

    results = ds_client.contentstore.secondary.text_search(
        query=test_data["question"],
        max_results=5,
        languages=["zz"],
    )
    assert len(results) == 0


def test_secondary_text_search_with_date(ds_client, test_data):
    """
    Test case for text secondary search with date.

    This test case performs a text secondary search with a specified date range.
    """
    start = datetime.fromisoformat("2024-01-01T00:00:00+00:00").astimezone(timezone.utc)
    end = datetime.fromisoformat("2024-03-01T00:00:00+00:00").astimezone(timezone.utc)

    text_results = ds_client.contentstore.secondary.text_search(
        query=test_data["question"],
        max_results=10,
        search_from_timestamp=start,
    )
    assert_date_range_filter(text_results, start_date=start)

    text_results = ds_client.contentstore.secondary.text_search(
        query=test_data["question"],
        max_results=10,
        search_to_timestamp=end,
    )
    assert_date_range_filter(text_results, end_date=end)

    text_results = ds_client.contentstore.secondary.text_search(
        query=test_data["question"],
        max_results=10,
        search_from_timestamp=start,
        search_to_timestamp=end,
    )
    assert_date_range_filter(text_results, start_date=start, end_date=end)


def test_secondary_text_search_descending(ds_client):
    """
    Test secondary text search with descending publication date sort order.
    Verifies results have valid IDs, sequential ranks, and descending dates.
    """
    results = ds_client.contentstore.secondary.text_search(
        query=None,
        max_results=10,
        sort_descending=True,
    )

    assert len(results) > 0
    for result in results:
        assert_valid_contentstore_result(result)
    assert_ranked_results(results)
    assert_descending_publication_dates(results)


def test_secondary_text_search_ascending(ds_client):
    """
    Test secondary text search with ascending publication date sort order.
    Verifies results have valid IDs, sequential ranks, and ascending dates.
    """

    results = ds_client.contentstore.secondary.text_search(
        query=None,
        max_results=10,
        sort_descending=False,
    )

    assert len(results) > 0
    for result in results:
        assert_valid_contentstore_result(result)
    assert_ranked_results(results)
    assert_ascending_publication_dates(results)


def test_secondary_vector_search(ds_client, test_data):
    """
    Test the secondary vector search function.

    This function tests the _secondary_vector_search function by calling it with a test embedding
    and asserting that the returned results have the expected length and properties.
    """
    results = ds_client.contentstore.secondary.vector_search(
        test_data["embedding"],
        max_results=5,
    )

    assert len(results) == 5
    for result in results:
        assert_valid_contentstore_result(result)
    assert_ascending_ranks(results)


def test_secondary_vector_search_with_date(ds_client, test_data):
    """
    Test case for vector secondary search with date.

    This test case performs a vector secondary search with a specified date range.
    """
    start = datetime.fromisoformat("2024-01-01T00:00:00+00:00").astimezone(timezone.utc)
    end = datetime.fromisoformat("2024-03-01T00:00:00+00:00").astimezone(timezone.utc)

    vector_results = ds_client.contentstore.secondary.vector_search(
        test_data["embedding"],
        max_results=10,
        search_from_timestamp=start,
    )
    assert_date_range_filter(vector_results, start_date=start)

    vector_results = ds_client.contentstore.secondary.vector_search(
        test_data["embedding"],
        max_results=10,
        search_to_timestamp=end,
    )
    assert_date_range_filter(vector_results, end_date=end)

    vector_results = ds_client.contentstore.secondary.vector_search(
        test_data["embedding"],
        max_results=10,
        search_from_timestamp=start,
        search_to_timestamp=end,
    )
    assert_date_range_filter(vector_results, start_date=start, end_date=end)


def test_secondary_vector_search_with_recency_low(ds_client, test_data):
    """
    Test the secondary vector search with a low recency weight.

    This test function performs a secondary vector search using a low recency weight
    and asserts that the results meet certain criteria especially
    that the score rank is identical to the final rank.
    """
    results = ds_client.contentstore.secondary.vector_search(
        test_data["embedding"],
        max_results=10,
        recency_weight=0.00001,
    )

    assert len(results) > 0
    for result in results:
        assert_valid_contentstore_result(result)
    assert_ranked_results(results)


def test_secondary_vector_search_with_recency_high(ds_client, test_data):
    """
    Test the secondary vector search with high recency weight.

    This test function performs a secondary vector search using a high recency weight
    and asserts that the returned results meet certain criteria, especially
    that the age rank is identical to the final rank.
    """
    results = ds_client.contentstore.secondary.vector_search(
        test_data["embedding"],
        max_results=10,
        recency_weight=0.99999,
    )

    assert len(results) > 0
    for result in results:
        assert_valid_contentstore_result(result)
    assert_ranked_results(results)


def test_secondary_hybrid_search_only_vector(ds_client, test_data):
    """
    Test the hybrid secondary search function with only query vector input.

    This test case verifies that the hybrid secondary search function returns the same results as the vector search function
    when only the query vector is provided as input.
    """
    hybrid_results = ds_client.contentstore.secondary.search(
        query=test_data["question"],
        max_results=5,
        vector_fraction=1.0,
        vector_weight=1.0,
        recency_weight=0.0,
    )

    vector_results = ds_client.contentstore.secondary.vector_search(
        test_data["embedding"],
        max_results=5,
    )

    assert len(hybrid_results) == 5
    for ix, hybrid_result in enumerate(hybrid_results):
        assert equal_results(hybrid_result, vector_results[ix])


def test_secondary_hybrid_search_only_text(ds_client, test_data):
    """
    Test case for performing hybrid search with only text query.

    This test case verifies that the hybrid search function returns the same results
    when performing a search using only the text query parameter, as a plain
    text query does.
    """
    hybrid_results = ds_client.contentstore.secondary.search(
        query=test_data["question"],
        max_results=5,
        vector_fraction=0.0,
        recency_weight=0.0,
    )

    text_results = ds_client.contentstore.secondary.text_search(
        query=test_data["question"],
        max_results=5,
    )

    assert len(hybrid_results) == 5
    for ix, hybrid_result in enumerate(hybrid_results):
        assert equal_results(hybrid_result, text_results[ix])


def test_secondary_hybrid_search(ds_client, test_data):
    """
    Test case for hybrid secondary search.

    This function tests the hybrid secondary search functionality by performing a search using both
    query embeddings and text queries. It compares the results from the hybrid search with the
    results from vector search and text search, ensuring that all the results from the hybrid
    search are present in the results from vector search and text search.
    """
    hybrid_results = ds_client.contentstore.secondary.search(
        query=test_data["question"],
        max_results=10,
    )

    vector_results = ds_client.contentstore.secondary.vector_search(
        query_embedding=test_data["embedding"],
        max_results=10,
    )

    text_results = ds_client.contentstore.secondary.text_search(
        query=test_data["question"],
        max_results=10,
    )

    hybrid_ids = [result.id for result in hybrid_results]

    contrib_ids = [result.id for result in vector_results]
    contrib_ids += [result.id for result in text_results]

    assert all([result in contrib_ids for result in hybrid_ids])


def test_secondary_hybrid_search_with_date(ds_client, test_data):
    """
    Test case for hybrid secondary search with date.

    This test case performs a hybrid secondary search with a specified date range.
    """
    start = datetime.fromisoformat("2024-01-01T00:00:00+00:00").astimezone(timezone.utc)
    end = datetime.fromisoformat("2024-03-01T00:00:00+00:00").astimezone(timezone.utc)

    hybrid_results = ds_client.contentstore.secondary.search(
        query=test_data["question"],
        max_results=10,
        search_from_timestamp=start,
    )
    assert_date_range_filter(hybrid_results, start_date=start)

    hybrid_results = ds_client.contentstore.secondary.search(
        query=test_data["question"],
        max_results=10,
        search_to_timestamp=end,
    )
    assert_date_range_filter(hybrid_results, end_date=end)

    hybrid_results = ds_client.contentstore.secondary.search(
        query=test_data["question"],
        max_results=10,
        search_from_timestamp=start,
        search_to_timestamp=end,
    )
    assert_date_range_filter(hybrid_results, start_date=start, end_date=end)


def test_secondary_hybrid_search_with_vector_high(ds_client, test_data):
    """
    Test case for performing hybrid search with a high vector weight, checking
    that the final ranking is that same as the vector ranking.
    """
    hybrid_results = ds_client.contentstore.secondary.search(
        query=test_data["question"],
        max_results=50,
        vector_weight=0.99999,
        vector_fraction=0.5,
        recency_weight=0.0,
    )

    vector_results = ds_client.contentstore.secondary.vector_search(
        query_embedding=test_data["embedding"],
        max_results=10,
    )

    for ix, result in enumerate(vector_results):
        assert equal_results(hybrid_results[ix], result)

def test_secondary_hybrid_search_with_evidence_filter(ds_client, test_data):
    """
    Test the secondary hybrid search function with evidence filter.

    This function tests the _secondary_hybrid_search function by calling it with a test embedding
    and asserting that the returned results have the expected length and properties. It also
    checks that the results have the expected evidence filter.
    """
    results = ds_client.contentstore.secondary.search(
        query=test_data["question"],
        max_results=50,
        apply_evidence_filter=True,
    )

    for result in results:
        assert_valid_contentstore_result(result)
    assert_ascending_ranks(results)
