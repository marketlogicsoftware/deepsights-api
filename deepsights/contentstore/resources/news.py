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
This module defines the resource to retrieve news content from the DeepSights API.
"""

from datetime import datetime
from typing import List

from deepsights.api import APIResource
from deepsights.contentstore.resources._download import contentstore_download
from deepsights.contentstore.resources._model import ContentStoreSearchResult
from deepsights.contentstore.resources._search import (
    contentstore_hybrid_search,
    contentstore_text_search,
    contentstore_vector_search,
)


#################################################
class NewsSearchResult(ContentStoreSearchResult):
    """
    Represents a search result of a news article in the content store.
    """


#################################################
class NewsResource(APIResource):
    """
    Represents a resource for retrieving news articles from the DeepSights content store.
    """

    def download(self, item_id: str) -> str:
        """
        Download the extracted text content of an item from the ContentStore.
        """
        return contentstore_download(self, item_id)

    #################################################
    def vector_search(
        self,
        query_embedding: List,
        min_score: float = 0.7,
        max_results: int = 100,
        languages: List[str] = None,
        recency_weight: float = 0.0,
        search_from_timestamp: datetime = None,
        search_to_timestamp: datetime = None,
        search_only_ai_allowed_content: bool = True,
    ) -> List[NewsSearchResult]:
        """
        Perform a vector-based search for news articles.

        Args:

            query_embedding (List): The embedding vector representing the query.
            min_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
            max_results (int, optional): The maximum number of search results to return. Defaults to 100.
            languages (List[str], optional): The list of languages to search for. Defaults to None.
            recency_weight (float, optional): The weight to apply to recency in the search ranking. Defaults to 0.0.
            search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
            search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.
            search_only_ai_allowed_content (bool, optional): Whether to search only AI-allowed content. Defaults to True.
        Returns:

            List[NewsSearchResult]: A list of search results as NewsSearchResult objects.
        """

        return contentstore_vector_search(
            self.api,
            item_type="NEWS",
            search_result=lambda i: NewsSearchResult(
                **dict(source_name=i["source"]["display_name"], **i)
            ),
            query_embedding=query_embedding,
            min_score=min_score,
            max_results=max_results,
            recency_weight=recency_weight,
            languages=languages,
            search_from_timestamp=search_from_timestamp,
            search_to_timestamp=search_to_timestamp,
            search_only_ai_allowed_content=search_only_ai_allowed_content,
        )

    #################################################
    def text_search(
        self,
        query: str,
        max_results: int = 100,
        offset: int = 0,
        languages: List[str] = None,
        sort_descending: bool = True,
        search_from_timestamp: datetime = None,
        search_to_timestamp: datetime = None,
        search_only_ai_allowed_content: bool = True,
    ) -> List[NewsSearchResult]:
        """
        Perform a text search for news articles in the DeepSights content store.

        Args:

            query (str): The search query.
            max_results (int, optional): The maximum number of search results to return. Defaults to 100.
            offset (int, optional): The offset to start the search from. Defaults to 0.
            languages (List[str], optional): The list of languages to search for. Defaults to None.
            sort_descending (bool, optional): Whether to sort the results in descending order. Defaults to True.
            search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
            search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.
            search_only_ai_allowed_content (bool, optional): Whether to search only AI-allowed content. Defaults to True.
        Returns:

            List[NewsSearchResult]: A list of news article search results.
        """
        return contentstore_text_search(
            self.api,
            item_type="NEWS",
            search_result=lambda i: NewsSearchResult(
                **dict(source_name=i["source"]["display_name"], **i)
            ),
            query=query,
            max_results=max_results,
            sort_descending=sort_descending,
            languages=languages,
            offset=offset,
            search_from_timestamp=search_from_timestamp,
            search_to_timestamp=search_to_timestamp,
            search_only_ai_allowed_content=search_only_ai_allowed_content,
        )

    #################################################
    def search(
        self,
        query: str,
        max_results: int = 100,
        languages: List[str] = None,
        min_vector_score: float = 0.7,
        vector_fraction: float = 0.85,
        vector_weight: float = 0.9,
        recency_weight: float = 0.0,
        search_from_timestamp: datetime = None,
        search_to_timestamp: datetime = None,
        search_only_ai_allowed_content: bool = True,
        apply_evidence_filter: bool = False,
    ) -> List[NewsSearchResult]:
        """
        Perform a contentstore hybrid search using the provided query.

        Args:

            query (str): The query.
            max_results (int, optional): The maximum number of search results to return. Defaults to 100.
            languages (List[str], optional): The list of languages to search for. Defaults to None.
            min_vector_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
            vector_fraction (float, optional): The fraction of the search results to be vector-based. Defaults to 0.85.
            vector_weight (float, optional): The weight to apply to vector search in result ranking. Defaults to 0.9.
            recency_weight (float, optional): The weight to apply to recency in result ranking. Defaults to 0.0.
            search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
            search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.
            search_only_ai_allowed_content (bool, optional): Whether to search only AI-allowed content. Defaults to True.
            apply_evidence_filter (bool, optional): Whether to apply the evidence filter. Defaults to False.
        Returns:

            List[NewsSearchResult]: The search results as a list of NewsSearchResult objects.
        """
        return contentstore_hybrid_search(
            self.api,
            item_type="NEWS",
            search_result=lambda i: NewsSearchResult(
                **dict(source_name=i["source"]["display_name"], **i)
            ),
            query=query,
            max_results=max_results,
            vector_weight=vector_weight,
            vector_fraction=vector_fraction,
            min_vector_score=min_vector_score,
            recency_weight=recency_weight,
            search_from_timestamp=search_from_timestamp,
            search_to_timestamp=search_to_timestamp,
            languages=languages,
            search_only_ai_allowed_content=search_only_ai_allowed_content,
            apply_evidence_filter=apply_evidence_filter,
        )
