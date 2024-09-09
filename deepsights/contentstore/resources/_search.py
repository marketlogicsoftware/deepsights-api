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
This module contains the base functions to search the ContentStore.
"""

from typing import List
from datetime import datetime
from pydantic import BaseModel
from deepsights.api import API
from deepsights.utils import (
    promote_exact_matches,
    rerank_by_recency,
)


#################################################
def _get_time_filter(search_from_timestamp: datetime, search_to_timestamp: datetime):
    """
    Returns a time filter dictionary based on the provided search_from_timestamp and search_to_timestamp.

    Args:
        search_from_timestamp (datetime): The starting timestamp for the search.
        search_to_timestamp (datetime): The ending timestamp for the search.

    Returns:
        dict: A time filter dictionary with "from" and "to" keys representing the search range.
              The values are ISO-formatted timestamps or None if the corresponding input is None.
    """
    time_filter = None
    if search_from_timestamp or search_to_timestamp:
        time_filter = {
            "from": (
                search_from_timestamp.isoformat() if search_from_timestamp else None
            ),
            "to": search_to_timestamp.isoformat() if search_to_timestamp else None,
        }
    return time_filter


#################################################
def contentstore_hybrid_search(
    api: API,
    query: str,
    item_type: str,
    search_result: BaseModel,
    max_results: int = 100,
    languages: List[str] = None,
    min_vector_score: float = 0.7,
    vector_fraction: float = 0.9,
    vector_weight: float = 0.9,
    recency_weight: float = 0.4,
    promote_exact_match: bool = False,
    search_from_timestamp: datetime = None,
    search_to_timestamp: datetime = None,
    search_only_ai_allowed_content: bool = True,
):
    """
    Perform a contentstore hybrid search using the provided query.

    Args:

        api (API): The DeepSights API instance.
        query (str): The query.
        item_type (str): The type of items to search for.
        search_result (BaseModel): The model to use for parsing search results.
        max_results (int, optional): The maximum number of search results to return. Defaults to 100.
        languages (List[str], optional): The languages to search for. Defaults to None.
        min_vector_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
        vector_fraction (float, optional): The fraction of the search results to be vector-based. Defaults to 0.9.
        vector_weight (float, optional): The weight to apply to vector search in result ranking. Defaults to 0.9.
        recency_weight (float, optional): The weight to apply to recency in result ranking. Defaults to 0.4.
        promote_exact_match (bool, optional): Whether to promote exact matches to the top of the results. Defaults to False.
        search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
        search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.
        search_only_ai_allowed_content (bool, optional): Whether to search only AI-allowed content. Defaults to True.

    Returns:

        List[BaseModel]: The re-ranked search results.
    """
    assert query, "The 'query' argument is required."
    assert 0 <= min_vector_score <= 1, "Minimum vector score must be between 0 and 1."
    assert 0 <= vector_fraction <= 1, "Vector fraction must be between 0 and 1"
    assert 0 <= vector_weight <= 1, "Vector weught must be between 0 and 1"
    assert 0 < max_results <= 250, "Maximum results must be between 1 and 250."
    assert (
        recency_weight is None or 0 <= recency_weight <= 1
    ), "Recency weight must be between 0 and 1."

    body = {
        "query": query,
        "source_items_type": item_type,
        "content_restrictions": "NONE",
        "limit": max_results,
        "vector_search_cut_off_score": min_vector_score,
        "alfa": vector_weight,
        "beta": 1.0 - recency_weight,
        "text_search_fraction": 1.0 - vector_fraction,
        "k": 60,
        "published_at": _get_time_filter(search_from_timestamp, search_to_timestamp),
        "languages": languages,
        "content_restrictions": (
            "ALLOWED_FOR_AI_SUMMARIZATION" if search_only_ai_allowed_content else "NONE"
        ),
    }
    response = api.post("item-service/items/_hybrid-search", body=body)

    # parse
    results = [search_result(i) for i in response["items"]]

    # pull exact matches to the top
    if promote_exact_match:
        results = promote_exact_matches(query, results)

    # record rank
    for rank, result in enumerate(results):
        result.rank = rank + 1

    return results


#################################################
def contentstore_vector_search(
    api: API,
    query_embedding: List,
    item_type: str,
    search_result: BaseModel,
    min_score: float = 0.7,
    max_results: int = 50,
    languages: List[str] = None,
    recency_weight: float = None,
    search_from_timestamp: datetime = None,
    search_to_timestamp: datetime = None,
    search_only_ai_allowed_content: bool = True,
):
    """
    Perform a contentstore vector search using the provided query embedding.

    Args:

        api (API): The DeepSights API instance.
        query_embedding (List): The query embedding vector.
        item_type (str): The type of items to search for.
        search_result (BaseModel): The model to use for parsing search results.
        min_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
        max_results (int, optional): The maximum number of search results to return. Defaults to 50.
        languages (List[str], optional): The languages to search for. Defaults to None.
        recency_weight (float, optional): The weight to apply to recency in result ranking. Defaults to None.
        search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
        search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.
        search_only_ai_allowed_content (bool, optional): Whether to search only AI-allowed content. Defaults to True.

    Returns:

        List[BaseModel]: The re-ranked search results.
    """
    assert query_embedding, "The 'query_embedding' argument is required."
    assert len(query_embedding) == 1536, "The 'query_embedding' must be of length 1536."
    assert 0 <= min_score <= 1, "Minimum score must be between 0 and 1."
    assert 0 < max_results <= 100, "Maximum results must be between 1 and 100."
    assert (
        recency_weight is None or 0 <= recency_weight <= 1
    ), "Recency weight must be between 0 and 1."

    body = {
        "vector": query_embedding,
        "source_items_type": item_type,
        "content_restrictions": "NONE",
        "limit": max_results,
        "score_lower_bound": min_score,
        "sort": "RELEVANCY_DESC",
        "languages": languages,
        "published_at": _get_time_filter(search_from_timestamp, search_to_timestamp),
        "content_restrictions": (
            "ALLOWED_FOR_AI_SUMMARIZATION" if search_only_ai_allowed_content else "NONE"
        ),
    }
    response = api.post("item-service/items/_vector-search", body=body)

    # parse
    results = [search_result(i) for i in response["items"]]

    # re-rank
    return rerank_by_recency(results, recency_weight=recency_weight)


#################################################
def contentstore_text_search(
    api: API,
    query: str,
    item_type: str,
    search_result: BaseModel,
    max_results: int = 50,
    offset: int = 0,
    languages: List[str] = None,
    recency_weight: float = None,
    search_from_timestamp: datetime = None,
    search_to_timestamp: datetime = None,
    search_only_ai_allowed_content: bool = True,
):
    """
    Perform a contentstore text search using the specified query and item type. If the query is None, the search will be sorted by publication date.

    Args:

        api (API): The DeepSights API instance.
        query (str): The search query.
        item_type (str): The type of items to search for.
        search_result (BaseModel): The model used to parse the search results.
        max_results (int, optional): The maximum number of results to return. Defaults to 50.
        offset (int, optional): The offset to start the search from. Defaults to 0.
        languages (List[str], optional): The languages to search for. Defaults to None.
        recency_weight (float, optional): The weight assigned to recency in result ranking. Defaults to None.
        search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
        search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.
        search_only_ai_allowed_content (bool, optional): Whether to search only AI-allowed content. Defaults to True.

    Returns:

        List[BaseModel]: The re-ranked search results.
    """
    assert 0 < max_results <= 100, "Maximum results must be between 1 and 100."
    assert (
        recency_weight is None or 0 <= recency_weight <= 1
    ), "Recency weight must be between 0 and 1."

    # force proper empty search
    if query is not None and len(query.strip()) == 0:
        query = None

    body = {
        "query": query,
        "source_items_type": item_type,
        "content_restrictions": "NONE",
        "limit": max_results,
        "offset": offset,
        "sort": "RELEVANCY_DESC" if query is not None else "PUBLISHED_AT_DESC",
        "languages": languages,
        "published_at": _get_time_filter(search_from_timestamp, search_to_timestamp),
        "content_restrictions": (
            "ALLOWED_FOR_AI_SUMMARIZATION" if search_only_ai_allowed_content else "NONE"
        ),
    }
    response = api.post("item-service/items/_text-search", body=body)

    # parse
    results = [search_result(i) for i in response["items"]]

    # re-rank
    return rerank_by_recency(results, recency_weight=recency_weight)
