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
This module contains the functions to retrieve secondary reports from the DeepSights content store.
"""

from typing import List

from deepsights.api import ContentStore
from deepsights.contentstore.model import SecondarySearchResult
from deepsights.contentstore._search import (
    contentstore_text_search,
    contentstore_vector_search,
    contentstore_search,
)


#################################################
def _secondary_vector_search(
    api: ContentStore,
    query_embedding: List,
    min_score: float = 0.7,
    max_results: int = 50,
    recency_weight: float = None,
):
    """
    Perform a vector-based search for secondary reports.

    Args:

        api (DeepSights): The DeepSights API instance.
        query_embedding (List): The embedding vector representing the query.
        min_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
        max_results (int, optional): The maximum number of search results to return. Defaults to 50.
        recency_weight (float, optional): The weight to apply to recency in the search ranking. Defaults to None.

    Returns:

        List[SecondaryReportSearchResult]: A list of search results as SecondaryReportSearchResult objects.
    """

    return contentstore_vector_search(
        api,
        item_type="REPORTS",
        search_result=lambda i: SecondarySearchResult(
            **dict(source_name=i["source"]["display_name"], **i)
        ),
        query_embedding=query_embedding,
        min_score=min_score,
        max_results=max_results,
        recency_weight=recency_weight,
    )


#################################################
def _secondary_text_search(
    api: ContentStore,
    query: str,
    max_results: int = 50,
    recency_weight: float = None,
):
    """
    Perform a text search for secondary reports in the DeepSights content store.

    Args:

        api (DeepSights): The DeepSights API instance.
        query (str): The search query.
        max_results (int, optional): The maximum number of search results to return. Defaults to 50.
        recency_weight (float, optional): The weight to assign to recency in the search ranking. Defaults to None.

    Returns:

        List[SecondaryReportSearchResult]: A list of news article search results.
    """
    return contentstore_text_search(
        api,
        item_type="REPORTS",
        search_result=lambda i: SecondarySearchResult(
            **dict(source_name=i["source"]["display_name"], **i)
        ),
        query=query,
        max_results=max_results,
        recency_weight=recency_weight,
    )


#################################################
def secondary_search(
    api: ContentStore,
    query: str = None,
    query_embedding: List = None,
    max_results: int = 50,
    recency_weight: float = None,
    vector_weight: float = 0.7,
    promote_exact_match: bool = False,
):
    """
    Perform a hybrid search for secondary reports in the content store.

    Args:

        api (ContentStore): The ContentStore API instance.
        query (str, optional): The search query. Defaults to None.
        query_embedding (List, optional): The query embedding. Defaults to None.
        max_results (int, optional): The maximum number of search results to return. Defaults to 50.
        recency_weight (float, optional): The weight for recency in the search ranking. Defaults to None.
        vector_weight (float, optional): The weight for vector similarity in the search ranking. Defaults to 0.7.
        promote_exact_match (bool, optional): Whether to promote exact matches in the search ranking. Defaults to False.

    Returns:
    
        List[SecondaryReportSearchResult]: The search results as a list of SecondaryReportSearchResult objects.
    """
    return contentstore_search(
        api,
        item_type="REPORTS",
        search_result=lambda i: SecondarySearchResult(
            **dict(source_name=i["source"]["display_name"], **i)
        ),
        query=query,
        query_embedding=query_embedding,
        max_results=max_results,
        recency_weight=recency_weight,
        vector_weight=vector_weight,
        promote_exact_match=promote_exact_match,
    )
