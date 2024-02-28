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
from concurrent.futures import ThreadPoolExecutor
from pydantic import BaseModel
from deepsights.api import ContentStore
from deepsights.utils import (
    rrf_merge_multi,
    promote_exact_matches,
    rerank_by_recency,
)


#################################################
def contentstore_vector_search(
    api: ContentStore,
    query_embedding: List,
    item_type: str,
    search_result: BaseModel,
    min_score: float = 0.7,
    max_results: int = 50,
    recency_weight: float = None,
):
    """
    Perform a contentstore vector search using the provided query embedding.

    Args:

        api (DeepSights): The DeepSights API instance.
        query_embedding (List): The query embedding vector.
        item_type (str): The type of items to search for.
        search_result (BaseModel): The model to use for parsing search results.
        min_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
        max_results (int, optional): The maximum number of search results to return. Defaults to 50.
        recency_weight (float, optional): The weight to apply to recency in result ranking. Defaults to None.

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
    }
    response = api.post("item-service/items/_vector-search", body=body)

    # parse
    results = [search_result(i) for i in response["items"]]

    # re-rank
    return rerank_by_recency(results, recency_weight=recency_weight)


#################################################
def contentstore_text_search(
    api: ContentStore,
    query: str,
    item_type: str,
    search_result: BaseModel,
    max_results: int = 50,
    recency_weight: float = None,
):
    """
    Perform a contentstore text search using the specified query and item type.

    Args:

        api (DeepSights): The DeepSights API instance.
        query (str): The search query.
        item_type (str): The type of items to search for.
        search_result (BaseModel): The model used to parse the search results.
        max_results (int, optional): The maximum number of results to return. Defaults to 50.
        recency_weight (float, optional): The weight assigned to recency in result ranking. Defaults to None.

    Returns:

        List[BaseModel]: The re-ranked search results.
    """
    assert query is not None, "Query must be provided."
    assert len(query) >= 1, "Query must be at least 2 characters."
    assert 0 < max_results <= 100, "Maximum results must be between 1 and 100."
    assert (
        recency_weight is None or 0 <= recency_weight <= 1
    ), "Recency weight must be between 0 and 1."

    body = {
        "query": query,
        "source_items_type": item_type,
        "content_restrictions": "NONE",
        "limit": max_results,
        "offset": 0,
        "sort": "RELEVANCY_DESC",
    }
    response = api.post("item-service/items/_text-search", body=body)

    # parse
    results = [search_result(i) for i in response["items"]]

    # re-rank
    return rerank_by_recency(results, recency_weight=recency_weight)


#################################################
def contentstore_search(
    api: ContentStore,
    item_type: str,
    search_result: BaseModel,
    query: str = None,
    query_embedding: List = None,
    max_results: int = 50,
    recency_weight: float = None,
    vector_weight: float = 0.7,
    promote_exact_match: bool = False,
) -> List[BaseModel]:
    """
    Perform a hybrid search combining text search and vector search.

    Args:

        api (ContentStore): The ContentStore API instance.
        item_type (str): The type of items to search for.
        search_result (BaseModel): The search result model.
        query (str, optional): The text query to search for. Defaults to None.
        query_embedding (List, optional): The vector query embedding. Defaults to None.
        max_results (int, optional): The maximum number of results to return. Defaults to 50.
        recency_weight (float, optional): The weight to assign to recency in the search ranking. Defaults to None.
        vector_weight (float, optional): The weight to assign to vector search in the search ranking. Defaults to 0.7.
        promote_exact_match (bool, optional): Whether to promote exact matches to the top of the results. Defaults to False.

    Returns:

        List[BaseModel]: The list of search results.
    """
    assert query or not promote_exact_match, "Promoting exact matches requires a query."

    results = []

    if query is None:
        if query_embedding is not None:
            # only vector search
            results = contentstore_vector_search(
                api,
                query_embedding=query_embedding,
                item_type=item_type,
                search_result=search_result,
                max_results=max_results,
                recency_weight=recency_weight,
            )
        else:
            raise ValueError("Must supply at least either text or vector.")
    elif query_embedding is None:
        # only text search
        results = contentstore_text_search(
            api,
            query=query,
            item_type=item_type,
            search_result=search_result,
            max_results=max_results,
            recency_weight=recency_weight,
        )
    else:
        # run a hybrid search in parallel threads
        with ThreadPoolExecutor(max_workers=2) as executor:
            text_future = executor.submit(
                contentstore_text_search,
                api=api,
                query=query,
                item_type=item_type,
                search_result=search_result,
                max_results=max_results,
                recency_weight=recency_weight,
            )
            vector_future = executor.submit(
                contentstore_vector_search,
                api=api,
                query_embedding=query_embedding,
                item_type=item_type,
                search_result=search_result,
                max_results=max_results,
                recency_weight=recency_weight,
            )

            text_search_results = text_future.result()
            vector_search_results = vector_future.result()

            # now rrf merge
            results = rrf_merge_multi(
                items=[text_search_results, vector_search_results],
                weights=(1 - vector_weight, vector_weight),
            )

    # pull exact matches to the top
    if promote_exact_match:
        results = promote_exact_matches(query, results)

    # re-record the rank
    for rank, result in enumerate(results):
        result.rank = rank + 1

    # cut off, we might have more results than requested due to the parallel search
    return results[:max_results]
