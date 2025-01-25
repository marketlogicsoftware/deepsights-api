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
This module contains the tests for the DeepSights ContentStore news search functionality.
"""

import json
import re
import shlex
from datetime import datetime, timezone

import deepsights

# get the test data from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    data = json.load(f)
    test_embedding = data["embedding"]
    test_query = data["question"]

# set up the API client
ds = deepsights.DeepSights()


def equal_results(result, other):
    # Need to allow for same title due to duplicate content sources
    return result.id == other.id or result.title == other.title


def test_news_text_search():
    """
    Test case for performing a text search on news content.

    This function tests the `text_search` method of the `ContentStore` class.
    It verifies that the search results contain the expected number of items,
    and that each result has a valid ID and source. It also checks that the rank
    of each result is greater than the rank of the previous result.

    Note: This test assumes the existence of a `test_query` variable.
    """
    results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=5,
    )

    assert len(results) == 5
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.source is not None

        if ix > 0:
            assert result.rank > results[ix - 1].rank


def test_news_text_empty_search():
    """ """
    results = ds.contentstore.news.text_search(
        query="",
        max_results=50,
    )

    assert len(results) == 50
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.source is not None

        if ix > 0:
            assert result.publication_date <= results[ix - 1].publication_date


def test_news_download():
    """ """
    results = ds.contentstore.news.text_search(
        query="",
        max_results=1,
    )

    content = ds.contentstore.news.download(results[0].id)
    assert len(content) > 0


def test_news_text_search_offset():
    """
    Test the news text search function with an offset.
    """
    results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=2,
    )
    offset_results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=1,
        offset=1,
    )
    for ix, result in enumerate(offset_results):
        assert equal_results(result, results[ix + 1])


def test_news_text_search_language():
    """
    Test the news text search function with a language filter.
    """
    results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=5,
        languages=["en"],
    )
    assert len(results) == 5
    for result in results:
        assert result.language == "en"

    results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=5,
        languages=["zz"],
    )
    assert len(results) == 0


def test_news_text_search_with_date():
    """
    Test case for text news search with date.

    This test case performs a text news search with a specified date range.
    """
    start = datetime.fromisoformat("2024-01-01T00:00:00+00:00").astimezone(timezone.utc)
    end = datetime.fromisoformat("2024-03-01T00:00:00+00:00").astimezone(timezone.utc)

    text_results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=10,
        search_from_timestamp=start,
    )
    for result in text_results:
        assert result.publication_date >= start

    text_results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=10,
        search_to_timestamp=end,
    )
    for result in text_results:
        assert result.publication_date <= end

    text_results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=10,
        search_from_timestamp=start,
        search_to_timestamp=end,
    )
    for result in text_results:
        assert result.publication_date <= end and result.publication_date >= start


def test_news_text_search_with_recency_low():
    """
    Test the news text search function with a low recency weight.

    This test verifies that the news text search function returns results
    when the recency weight is set to a low value. It checks that the
    returned results have valid IDs, ranks, score ranks, and age ranks,
    and that the final rank is identical to the score rank.

    Note: This test assumes the existence of a `test_query` variable.
    """

    results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=10,
        recency_weight=0.00001,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1


def test_news_text_search_with_recency_high():
    """
    Test the news text search function with a high recency weight.

    This test verifies that the news text search function returns results
    when the recency weight is set to a high value. It checks that the
    returned results have valid IDs, ranks, score ranks, and age ranks,
    and that the final rank is identical to the age rank.

    Note: This test assumes the existence of a `test_query` variable.
    """
    results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=10,
        recency_weight=0.99999,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1


def test_news_vector_search():
    """
    Test the news vector search function.

    This function tests the _news_vector_search function by calling it with a test embedding
    and asserting that the returned results have the expected length and properties.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = ds.contentstore.news.vector_search(
        test_embedding,
        max_results=5,
    )

    assert len(results) == 5
    for ix, result in enumerate(results):
        assert result.id is not None

        if ix > 0:
            assert result.rank > results[ix - 1].rank


def test_news_vector_search_with_date():
    """
    Test case for vector news search with date.

    This test case performs a vector news search with a specified date range.
    """
    start = datetime.fromisoformat("2024-01-01T00:00:00+00:00").astimezone(timezone.utc)
    end = datetime.fromisoformat("2024-03-01T00:00:00+00:00").astimezone(timezone.utc)

    vector_results = ds.contentstore.news.vector_search(
        test_embedding,
        max_results=10,
        search_from_timestamp=start,
    )
    for result in vector_results:
        assert result.publication_date >= start

    vector_results = ds.contentstore.news.vector_search(
        test_embedding,
        max_results=10,
        search_to_timestamp=end,
    )
    for result in vector_results:
        assert result.publication_date <= end

    vector_results = ds.contentstore.news.vector_search(
        test_embedding,
        max_results=10,
        search_from_timestamp=start,
        search_to_timestamp=end,
    )
    for result in vector_results:
        assert result.publication_date <= end and result.publication_date >= start


def test_news_vector_search_with_recency_low():
    """
    Test the news vector search with a low recency weight.

    This test function performs a news vector search using a low recency weight
    and asserts that the results meet certain criteria especially
    that the score rank is identical to the final rank.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = ds.contentstore.news.vector_search(
        test_embedding,
        max_results=10,
        recency_weight=0.00001,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1


def test_news_vector_search_with_recency_high():
    """
    Test the news vector search with high recency weight.

    This test function performs a news vector search using a high recency weight
    and asserts that the returned results meet certain criteria, especially
    that the age rank is identical to the final rank.

    Note: This test assumes the existence of a `test_embedding` variable.
    """
    results = ds.contentstore.news.vector_search(
        test_embedding,
        max_results=10,
        recency_weight=0.99999,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1


def test_news_hybrid_search_only_vector():
    """
    Test the hybrid news search function with only vector and no recency reranking.

    This test case verifies that the hybrid news search function returns the same results as the vector search function
    when only the vector content  is used.

    Note: This test assumes the existence of a `test_embedding` and `test_query` variable.
    """
    hybrid_results = ds.contentstore.news.search(
        query=test_query,
        max_results=5,
        vector_weight=1.0,
        vector_fraction=1.0,
        recency_weight=0.0,
    )

    vector_results = ds.contentstore.news.vector_search(
        test_embedding,
        max_results=5,
        recency_weight=0.0,
    )

    assert len(hybrid_results) == 5
    for ix, hybrid_result in enumerate(hybrid_results):
        assert equal_results(hybrid_result, vector_results[ix])


def test_news_hybrid_search_only_text():
    """
    Test case for performing hybrid search with only text query.

    This test case verifies that the hybrid search function returns the same results
    when performing a search using only the text results, as a plain
    text query does.

    Note: This test assumes the existence of a `test_query` variable.
    """

    results = 3
    hybrid_results = ds.contentstore.news.search(
        query=test_query,
        max_results=results,
        vector_fraction=0.0,
        vector_weight=0.0,
        recency_weight=0.0,
    )

    text_results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=results,
        recency_weight=0.0,
    )

    assert len(hybrid_results) == results
    for ix, hybrid_result in enumerate(hybrid_results):
        assert equal_results(hybrid_result, text_results[ix])


def test_news_hybrid_search():
    """
    Test case for hybrid news search.

    This function tests the hybrid news search functionality by performing a search using both
    query embeddings and text queries. It compares the results from the hybrid search with the
    results from vector search and text search, ensuring that all the results from the hybrid
    search are present in the results from vector search and text search.

    Note: This test assumes the existence of `test_embedding` and `test_query` variables.
    """
    hybrid_results = ds.contentstore.news.search(
        query=test_query,
        max_results=10,
    )

    vector_results = ds.contentstore.news.vector_search(
        query_embedding=test_embedding,
        max_results=10,
    )

    text_results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=10,
    )

    assert len(hybrid_results) == 10

    hybrid_ids = [result.id for result in hybrid_results]

    contrib_ids = [result.id for result in vector_results]
    contrib_ids += [result.id for result in text_results]

    assert all([result in contrib_ids for result in hybrid_ids])


def test_news_hybrid_search_with_date():
    """
    Test case for hybrid news search with date.

    This test case performs a hybrid news search with a specified date range.
    """
    start = datetime.fromisoformat("2024-01-01T00:00:00+00:00").astimezone(timezone.utc)
    end = datetime.fromisoformat("2024-03-01T00:00:00+00:00").astimezone(timezone.utc)

    hybrid_results = ds.contentstore.news.search(
        query=test_query,
        max_results=10,
        search_from_timestamp=start,
    )
    for result in hybrid_results:
        assert result.publication_date >= start

    hybrid_results = ds.contentstore.news.search(
        query=test_query,
        max_results=10,
        search_to_timestamp=end,
    )
    for result in hybrid_results:
        assert result.publication_date <= end

    hybrid_results = ds.contentstore.news.search(
        query=test_query,
        max_results=10,
        search_from_timestamp=start,
        search_to_timestamp=end,
    )
    for result in hybrid_results:
        assert result.publication_date <= end and result.publication_date >= start


def test_news_hybrid_search_with_vector_high():
    """
    Test case for performing hybrid search with a high vector weight, checking
    that the final ranking is that same as the vector ranking.

    Note: This test assumes the existence of `test_embedding` and `test_query` variables.
    """
    hybrid_results = ds.contentstore.news.search(
        query=test_query,
        max_results=10,
        vector_weight=0.99999,
        vector_fraction=1.0,
        recency_weight=0.0,
    )

    vector_results = ds.contentstore.news.vector_search(
        query_embedding=test_embedding,
        max_results=10,
        recency_weight=0.0,
    )

    assert len(hybrid_results) == 10
    for ix, result in enumerate(hybrid_results):
        assert equal_results(result, vector_results[ix])


def test_news_hybrid_search_with_vector_low():
    """
    Test case for performing hybrid search with a low vector weight, checking
    that the final ranking is that same as the text ranking.

    Note: This test assumes the existence of `test_embedding` and `test_query` variables.
    """

    results = 3
    hybrid_results = ds.contentstore.news.search(
        query=test_query,
        max_results=results,
        vector_weight=0.00001,
        vector_fraction=0.0,
        recency_weight=0.0,
    )

    text_results = ds.contentstore.news.text_search(
        query=test_query,
        max_results=results,
        recency_weight=0.0,
    )

    assert len(hybrid_results) == results
    for ix, result in enumerate(hybrid_results):
        assert equal_results(result, text_results[ix])


def test_news_text_search_with_title_promotion():
    """
    Test case for performing a news text search with title promotion.

    This test case verifies that the hybrid search function returns the expected results
    when searching for news articles based on a query with title promotion enabled.
    """
    query = "gen candy"

    # first find top 10 results without title promotion and hard recency weight
    hybrid_results_no_promotion = ds.contentstore.news.search(
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
    assert ix < len(hybrid_results_no_promotion) - 1

    # now retrieve with title promotion
    hybrid_results = ds.contentstore.news.search(
        query=query,
        max_results=50,
        promote_exact_match=True,
        recency_weight=0.99,
    )

    assert equal_results(hybrid_results[0], hybrid_results_no_promotion[ix])
    assert matches(query, hybrid_results[0])
