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
This module defines the resource to retrieve news content from the DeepSights API.
"""

from typing import List
from datetime import datetime

from deepsights.api import APIResource
from deepsights.contentstore.resources._model import ContentStoreSearchResult
from deepsights.contentstore.resources._search import (
    contentstore_text_search,
    contentstore_vector_search,
    contentstore_hybrid_search,
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

    #################################################
    def vector_search(
        self,
        query_embedding: List,
        min_score: float = 0.7,
        max_results: int = 30,
        languages: List[str] = None,
        recency_weight: float = None,
        search_from_timestamp: datetime = None,
        search_to_timestamp: datetime = None,
    ):
        """
        Perform a vector-based search for news articles.

        Args:

            query_embedding (List): The embedding vector representing the query.
            min_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
            max_results (int, optional): The maximum number of search results to return. Defaults to 30.
            languages (List[str], optional): The list of languages to search for. Defaults to None.
            recency_weight (float, optional): The weight to apply to recency in the search ranking. Defaults to None.
            search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
            search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.

        Returns:

            List[NewsArticleSearchResult]: A list of search results as NewsArticleSearchResult objects.
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
        )

    #################################################
    def text_search(
        self,
        query: str,
        max_results: int = 30,
        offset: int = 0,
        languages: List[str] = None,
        recency_weight: float = None,
        search_from_timestamp: datetime = None,
        search_to_timestamp: datetime = None,
    ):
        """
        Perform a text search for news articles in the DeepSights content store.

        Args:

            query (str): The search query.
            max_results (int, optional): The maximum number of search results to return. Defaults to 30.
            offset (int, optional): The offset to start the search from. Defaults to 0.
            languages (List[str], optional): The list of languages to search for. Defaults to None.
            recency_weight (float, optional): The weight to assign to recency in the search ranking. Defaults to None.
            search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
            search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.

        Returns:

            List[NewsArticleSearchResult]: A list of news article search results.
        """
        return contentstore_text_search(
            self.api,
            item_type="NEWS",
            search_result=lambda i: NewsSearchResult(
                **dict(source_name=i["source"]["display_name"], **i)
            ),
            query=query,
            max_results=max_results,
            recency_weight=recency_weight,
            languages=languages,
            offset=offset,
            search_from_timestamp=search_from_timestamp,
            search_to_timestamp=search_to_timestamp,
        )

    #################################################
    def search(
        self,
        query: str,
        max_results: int = 30,
        languages: List[str] = None,
        min_vector_score: float = 0.7,
        vector_fraction: float = 0.9,
        vector_weight: float = 0.9,
        recency_weight: float = 0.4,
        promote_exact_match: bool = False,
        search_from_timestamp: datetime = None,
        search_to_timestamp: datetime = None,
    ):
        """
        Perform a contentstore hybrid search using the provided query.

        Args:

            query (str): The query.
            search_result (BaseModel): The model to use for parsing search results.
            max_results (int, optional): The maximum number of search results to return. Defaults to 30.
            languages (List[str], optional): The list of languages to search for. Defaults to None.
            min_vector_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
            vector_fraction (float, optional): The fraction of the search results to be vector-based. Defaults to 0.9.
            vector_weight (float, optional): The weight to apply to vector search in result ranking. Defaults to 0.9.
            recency_weight (float, optional): The weight to apply to recency in result ranking. Defaults to 0.4.
            promote_exact_match (bool, optional): Whether to promote exact matches in the search ranking. Defaults to False.
            search_from_timestamp (datetime, optional): The start timestamp for the search. Defaults to None.
            search_to_timestamp (datetime, optional): The end timestamp for the search. Defaults to None.

        Returns:

            List[NewsArticleSearchResult]: The search results as a list of NewsArticleSearchResult objects.
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
            promote_exact_match=promote_exact_match,
            search_from_timestamp=search_from_timestamp,
            search_to_timestamp=search_to_timestamp,
            languages=languages,
        )
