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
This module contains the functions to search for documents and document pages based on their vector embeddings.
"""

from typing import List
from deepsights.api import APIResource
from deepsights.utils import rerank_by_recency, promote_exact_matches
from deepsights.documentstore.resources.documents._model import (
    DocumentPageSearchResult,
    DocumentSearchResult,
)
from deepsights.documentstore.resources.documents._load import (
    documents_load,
    document_pages_load,
)


#################################################
def document_pages_search(
    resource: APIResource,
    query_embedding: List,
    min_score: float = 0.7,
    max_results: int = 50,
    load_pages=False,
):
    """
    Searches for document pages based on their vector embeddings.

    Args:

        resource (APIResource): An instance of the DeepSights API resource.
        query_embedding (List): The query vector embedding.
        min_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
        max_results (int, optional): The maximum number of search results to return. Defaults to 50.
        load_pages (bool, optional): Whether to load the pages associated with the search results. Defaults to False.

    Returns:

        List[DocumentPageSearchResult]: The list of DocumentPageSearchResult objects representing the search results.
    """
    assert query_embedding, "The 'query_embedding' argument is required."
    assert len(query_embedding) == 1536, "The 'query_embedding' must be of length 1536."
    assert 0 <= min_score <= 1, "The 'min_score' must be between 0 and 1."
    assert 0 < max_results <= 100, "Maximum results must be between 1 and 100."

    body = {
        "embeddings": query_embedding,
        "min_score": min_score,
        "limit": max_results,
    }
    params = {"ai_model": "ADA", "search_model": "PAGE"}
    response = resource.api.post(
        "vector-search-service/vectors/_search", params=params, body=body
    )

    # parse
    results = [
        DocumentPageSearchResult(
            document_id=d["artifact_id"], id=p["part_id"], score=p["score"]
        )
        for d in response["results"]
        for p in d["result_parts"]
    ]

    # make sure we are sorted by score
    results.sort(key=lambda x: x.score, reverse=True)

    # load pages if requested
    if load_pages:
        # make sure pages are loaded
        document_pages_load(resource, page_ids=[r.id for r in results])

    return results


#################################################
def documents_search(
    resource: APIResource,
    query: str = None,
    query_embedding: List = None,
    min_score: float = 0.7,
    max_results: int = 50,
    recency_weight: float = None,
    promote_exact_match: bool = False,
    load_documents=False,
):
    """
    Searches for document based on their vector embeddings.

    Args:

        resource (APIResource): An instance of the DeepSights API resource.
        query (str): The search query; currently only used for promoting exact matches.
        query_embedding (List): The query vector embedding.
        min_score (float, optional): The minimum score threshold for document matches. Defaults to 0.7.
        max_results (int, optional): The maximum number of document matches to return. Defaults to 50.
        recency_weight (float, optional): The weight to apply to the recency factor in ranking. Defaults to None, i.e. no recency weighting.
        promote_exact_match (bool, optional): Whether to promote exact matches to the top of the search results. Defaults to False.
        load_documents (bool, optional): Whether to load documents and matching pages associated with the search results. Defaults to False.

    Returns:

        List: The DocumentSearchResults.
    """
    assert query_embedding, "The 'query_embedding' argument is required."
    assert len(query_embedding) == 1536, "The 'query_embedding' must be of length 1536."
    assert 0 <= min_score <= 1, "The 'min_score' must be between 0 and 1."
    assert 0 < max_results <= 100, "Maximum results must be between 1 and 100."
    assert (
        recency_weight is None or 0 <= recency_weight <= 1
    ), "Recency weight must be between 0 and 1."
    assert (
        query is None or promote_exact_matches
    ), "The 'query' argument is only used when 'promote_exact_match' is set to True."

    # get the page matches
    page_matches = document_pages_search(
        resource,
        query_embedding,
        min_score=min_score,
        max_results=max_results,
        load_pages=load_documents,
    )

    # calculate aggregated document rank score
    document_rank_score = {}
    for rank, page in enumerate(page_matches):
        document_rank_score[page.document_id] = document_rank_score.get(
            page.document_id, 0
        ) + 1.0 / (rank + max_results / 2)

    document_rank_score = {
        k: v
        for k, v in sorted(
            document_rank_score.items(), key=lambda item: item[1], reverse=True
        )
    }

    # now construct the document matches in rank order
    results = [
        DocumentSearchResult(
            id=document_id,
            page_matches=[p for p in page_matches if p.document_id == document_id],
        )
        for rank, document_id in enumerate(document_rank_score)
    ]

    # load documents if requested
    if load_documents or recency_weight:
        # make sure the documents are loaded
        documents_load(resource, document_ids=[r.id for r in results])

        # load pages if requested
        if load_documents:
            page_ids = [p.id for r in results for p in r.page_matches]
            document_pages_load(resource, page_ids=page_ids)

            # order pages by their number
            for r in results:
                r.page_matches.sort(key=lambda x: x.page_number)

        # apply recency weight
        results = rerank_by_recency(results, recency_weight=recency_weight)

    # pull exact matches to the top
    if promote_exact_match and query:
        results = promote_exact_matches(query, results)

    # record rank
    for rank, result in enumerate(results):
        result.rank = rank + 1

    return results
