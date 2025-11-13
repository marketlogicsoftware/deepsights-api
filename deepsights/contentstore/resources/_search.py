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
This module contains the base functions to search the ContentStore.
"""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, TypeVar

from pydantic import BaseModel

from deepsights.api import API
from deepsights.utils import (
    rerank_by_recency,
)


# ----------------------------
# Validation helpers (internal)
# ----------------------------
def _validate_query_non_empty(query: str, max_len: int = 1000) -> str:
    """Validate that query is a non-empty string with a max length; return stripped.

    Mirrors existing error messages to avoid behavioral changes.
    """
    if not isinstance(query, str):
        raise ValueError("Query must be a string")
    q = query.strip()
    if len(q) == 0:
        raise ValueError("Query cannot be empty")
    if len(q) > max_len:
        raise ValueError(f"Query too long (max {max_len} characters)")
    return q


def _ensure_between_0_1(value: float, message: str) -> None:
    if not 0 <= value <= 1:
        raise ValueError(message)


def _validate_max_results(value: int, upper: int, message: str) -> None:
    if not 0 < value <= upper:
        raise ValueError(message)


def _validate_embedding(query_embedding: List) -> None:
    if not isinstance(query_embedding, list):
        raise ValueError("Query embedding must be a list")
    if not query_embedding:
        raise ValueError("Query embedding cannot be empty")
    if len(query_embedding) != 1536:
        raise ValueError("Query embedding must be of length 1536")


#################################################
def _get_time_filter(
    search_from_timestamp: Optional[datetime], search_to_timestamp: Optional[datetime]
) -> Optional[Dict[str, Optional[str]]]:
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
            "from": (search_from_timestamp.isoformat() if search_from_timestamp else None),
            "to": search_to_timestamp.isoformat() if search_to_timestamp else None,
        }
    return time_filter


#################################################
T = TypeVar("T", bound=BaseModel)


# pylint: disable-next=too-many-arguments, too-many-positional-arguments, too-many-locals
def contentstore_hybrid_search(
    api: API,
    query: str,
    item_type: str,
    search_result: Callable[[Any], T],
    max_results: int = 100,
    languages: Optional[List[str]] = None,
    min_vector_score: float = 0.7,
    vector_fraction: float = 0.85,
    vector_weight: float = 0.9,
    recency_weight: float = 0.0,
    search_from_timestamp: Optional[datetime] = None,
    search_to_timestamp: Optional[datetime] = None,
    apply_evidence_filter: bool = False,
    search_only_ai_allowed_content: bool = True,
) -> List[T]:
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
        vector_fraction (float, optional): The fraction of the search results to be vector-based. Defaults to 0.85.
        vector_weight (float, optional): The weight to apply to vector search in result ranking. Defaults to 0.9.
        recency_weight (float, optional): The weight to apply to recency in result ranking. Defaults to 0.0.
        search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
        search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.
        apply_evidence_filter (bool, optional): Whether to apply the evidence filter. Defaults to False.
        search_only_ai_allowed_content (bool, optional): Whether to search only AI-allowed content. Defaults to True.

    Returns:

        List[BaseModel]: The re-ranked search results.
    """
    # Input validation
    query = _validate_query_non_empty(query, max_len=1000)
    _ensure_between_0_1(min_vector_score, "Minimum vector score must be between 0 and 1")
    _ensure_between_0_1(vector_fraction, "Vector fraction must be between 0 and 1")
    _ensure_between_0_1(vector_weight, "Vector weight must be between 0 and 1")
    _validate_max_results(max_results, 250, "Maximum results must be between 1 and 250")
    _ensure_between_0_1(recency_weight, "Recency weight must be between 0 and 1")

    body = {
        "query": query,
        "source_items_type": item_type,
        "limit": max_results,
        "vector_search_cut_off_score": min_vector_score,
        "alfa": vector_weight,
        "beta": 1.0 - recency_weight,
        "text_search_fraction": 1.0 - vector_fraction,
        "k": 60,
        "published_at": _get_time_filter(search_from_timestamp, search_to_timestamp),
        "languages": languages,
        "content_restrictions": ("ALLOWED_FOR_AI_SUMMARIZATION" if search_only_ai_allowed_content else "NONE"),
        "use_evidence_filtering": apply_evidence_filter,
    }
    response = api.post("item-service/items/_hybrid-search", body=body)

    # parse
    results: List[T] = [search_result(i) for i in response["items"]]

    # record rank
    for rank, result in enumerate(results):
        if hasattr(result, "rank"):
            result.rank = rank + 1

    return results


#################################################
# pylint: disable-next=too-many-arguments, too-many-positional-arguments
def contentstore_vector_search(
    api: API,
    query_embedding: List,
    item_type: str,
    search_result: Callable[[Any], T],
    min_score: float = 0.7,
    max_results: int = 100,
    languages: Optional[List[str]] = None,
    recency_weight: float = 0.0,
    search_from_timestamp: Optional[datetime] = None,
    search_to_timestamp: Optional[datetime] = None,
    search_only_ai_allowed_content: bool = True,
) -> List[T]:
    """
    Perform a contentstore vector search using the provided query embedding.

    Args:

        api (API): The DeepSights API instance.
        query_embedding (List): The query embedding vector.
        item_type (str): The type of items to search for.
        search_result (BaseModel): The model to use for parsing search results.
        min_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
        max_results (int, optional): The maximum number of search results to return. Defaults to 100.
        languages (List[str], optional): The languages to search for. Defaults to None.
        recency_weight (float, optional): The weight to apply to recency in result ranking. Defaults to 0.0.
        search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
        search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.
        search_only_ai_allowed_content (bool, optional): Whether to search only AI-allowed content. Defaults to True.

    Returns:

        List[BaseModel]: The re-ranked search results.
    """
    # Input validation
    _validate_embedding(query_embedding)
    _ensure_between_0_1(min_score, "Minimum score must be between 0 and 1")
    _validate_max_results(max_results, 100, "Maximum results must be between 1 and 100")
    _ensure_between_0_1(recency_weight, "Recency weight must be between 0 and 1")

    body = {
        "vector": query_embedding,
        "source_items_type": item_type,
        "limit": max_results,
        "score_lower_bound": min_score,
        "sort": "RELEVANCY_DESC",
        "languages": languages,
        "published_at": _get_time_filter(search_from_timestamp, search_to_timestamp),
        "content_restrictions": ("ALLOWED_FOR_AI_SUMMARIZATION" if search_only_ai_allowed_content else "NONE"),
    }
    response = api.post("item-service/items/_vector-search", body=body)

    # parse
    results: List[T] = [search_result(i) for i in response["items"]]

    # re-rank
    return rerank_by_recency(results, recency_weight=recency_weight)


#################################################
# pylint: disable-next=too-many-arguments, too-many-positional-arguments, too-many-locals
def contentstore_text_search(
    api: API,
    query: Optional[str],
    item_type: str,
    search_result: Callable[[Any], T],
    max_results: int = 100,
    offset: int = 0,
    languages: Optional[List[str]] = None,
    sort_descending: bool = True,
    search_from_timestamp: Optional[datetime] = None,
    search_to_timestamp: Optional[datetime] = None,
    search_only_ai_allowed_content: bool = True,
) -> List[T]:
    """
    Perform a contentstore text search using the specified query and item type. If the query is None,
    the search will be sorted by publication date.

    Args:

        api (API): The DeepSights API instance.
        query (str): The search query.
        item_type (str): The type of items to search for.
        search_result (BaseModel): The model used to parse the search results.
        max_results (int, optional): The maximum number of results to return. Defaults to 100.
        offset (int, optional): The offset to start the search from. Defaults to 0.
        languages (List[str], optional): The languages to search for. Defaults to None.
        sort_descending (bool, optional): Whether to sort results in descending order (relevancy or publication date). Defaults to True.
        search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
        search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.
        search_only_ai_allowed_content (bool, optional): Whether to search only AI-allowed content. Defaults to True.

    Returns:

        List[BaseModel]: The re-ranked search results.
    """
    _validate_max_results(max_results, 100, "Maximum results must be between 1 and 100")

    # force proper empty search
    if query is not None and len(query.strip()) == 0:
        query = None

    # determine sort order
    if query is not None:
        sort_order = "RELEVANCY_DESC" if sort_descending else "RELEVANCY_ASC"
    else:
        sort_order = "PUBLISHED_AT_DESC" if sort_descending else "PUBLISHED_AT_ASC"

    body = {
        "query": query,
        "source_items_type": item_type,
        "limit": max_results,
        "offset": offset,
        "sort": sort_order,
        "languages": languages,
        "published_at": _get_time_filter(search_from_timestamp, search_to_timestamp),
        "content_restrictions": ("ALLOWED_FOR_AI_SUMMARIZATION" if search_only_ai_allowed_content else "NONE"),
    }
    response = api.post("item-service/items/_text-search", body=body)

    # parse
    results: List[T] = [search_result(i) for i in response["items"]]

    # record rank
    for rank, result in enumerate(results):
        if hasattr(result, "rank"):
            result.rank = rank + 1

    return results
