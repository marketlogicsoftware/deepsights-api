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
This module contains the functions to perform topic searches via the DeepSights API.
"""

from typing import List

from deepsights.api import APIResource
from deepsights.userclient.resources.search._model import TopicSearchResult


#################################################
class SearchResource(APIResource):
    """
    Represents a resource for performing topic searches via the DeepSights API.
    """

    #################################################
    def topic_search(
        self, query: str, extended_search: bool = False
    ) -> List[TopicSearchResult]:
        """
        Searches for documents by topic using AI-powered analysis.

        Args:
            query (str): The search query topic.
            extended_search (bool, optional): Whether to perform extended search. Defaults to False.

        Returns:
            List[TopicSearchResult]: The list of topic search results.
        """
        # Input validation
        if not isinstance(query, str):
            raise ValueError("The 'query' must be a string.")
        query = query.strip()
        if len(query) == 0:
            raise ValueError("The 'query' cannot be empty.")
        if len(query) > 100:
            raise ValueError("The 'query' must be 100 characters or less.")

        body = {
            "query": query,
            "extended_search": extended_search,
        }

        response = self.api.post("end-user-gateway-service/topic-searches", body=body)

        # Extract the search results from the response
        search_results = response.get("context", {}).get("search_results", [])
        return [TopicSearchResult(**result) for result in search_results if len(result) > 0]
