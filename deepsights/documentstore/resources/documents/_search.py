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
This module contains the functions to search for documents and document pages based on their vector embeddings.
"""

import warnings
from datetime import datetime
from typing import List, Optional

from deepsights.api import APIResource
from deepsights.documentstore.resources.documents._load import (
    document_pages_load,
    documents_load,
)
from deepsights.documentstore.resources.documents._model import (
    DocumentPageSearchResult,
    DocumentSearchResult,
    HybridSearchResult,
    TaxonomyFilter,
    TextSearchResult,
    TopicSearchResult,
)
from deepsights.utils import promote_exact_matches, rerank_by_recency

TEXT_SEARCH_METADATA_FIELDS = ("title", "file_name", "source", "summary")
TEXT_SEARCH_SORT_OPTIONS = ("RELEVANCY", "RECENCY")
MAX_TEXT_SEARCH_QUERY_LENGTH = 512


#################################################
def document_pages_search(
    resource: APIResource,
    query_embedding: List,
    min_score: float = 0.7,
    max_results: int = 50,
    load_pages: bool = False,
) -> List[DocumentPageSearchResult]:
    """
    Searches for document pages based on their vector embeddings.

    Deprecated: This function will be removed in a future version.
    Use `hybrid_search()` via `ds.documentstore.documents.search(query=...)` instead.

    Args:

        resource (APIResource): An instance of the DeepSights API resource.
        query_embedding (List): The query vector embedding.
        min_score (float, optional): The minimum score threshold for search results. Defaults to 0.7.
        max_results (int, optional): The maximum number of search results to return. Defaults to 50.
        load_pages (bool, optional): Whether to load the pages associated with the search results. Defaults to False.

    Returns:

        List[DocumentPageSearchResult]: The list of DocumentPageSearchResult objects representing the search results.
    """
    # Input validation
    if not query_embedding:
        raise ValueError("The 'query_embedding' argument is required.")
    if len(query_embedding) != 1536:
        raise ValueError("The 'query_embedding' must be of length 1536.")
    if not 0 <= min_score <= 1:
        raise ValueError("The 'min_score' must be between 0 and 1.")
    if not 0 < max_results <= 100:
        raise ValueError("Maximum results must be between 1 and 100.")

    # emit deprecation warning
    warnings.warn(
        "document_pages_search() is deprecated and will be removed in a future version. Use hybrid_search() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    body = {
        "embeddings": query_embedding,
        "min_score": min_score,
        "limit": max_results,
    }
    params = {"ai_model": "ADA", "search_model": "PAGE"}
    response = resource.api.post("vector-search-service/vectors/_search", params=params, body=body)

    # parse
    results = [
        DocumentPageSearchResult(document_id=d["artifact_id"], id=p["part_id"], score=p["score"])
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
    query: str | None = None,
    query_embedding: List | None = None,
    min_score: float = 0.7,
    max_results: int = 50,
    recency_weight: float | None = None,
    promote_exact_match: bool = False,
    load_documents: bool = False,
) -> List[DocumentSearchResult]:
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
    # Input validation
    if not query_embedding:
        raise ValueError("The 'query_embedding' argument is required.")
    if len(query_embedding) != 1536:
        raise ValueError("The 'query_embedding' must be of length 1536.")
    if not 0 <= min_score <= 1:
        raise ValueError("The 'min_score' must be between 0 and 1.")
    if not 0 < max_results <= 100:
        raise ValueError("Maximum results must be between 1 and 100.")
    if recency_weight is not None and not 0 <= recency_weight <= 1:
        raise ValueError("Recency weight must be between 0 and 1.")
    if query is not None and not promote_exact_match:
        raise ValueError("The 'query' argument is only used when 'promote_exact_match' is set to True.")

    # emit deprecation warning
    warnings.warn(
        "documents_search() is deprecated and will be removed in a future version. Use hybrid_search() instead.",
        DeprecationWarning,
        stacklevel=2,
    )

    # get the page matches
    page_matches = document_pages_search(
        resource,
        query_embedding,
        min_score=min_score,
        max_results=max_results,
        load_pages=load_documents,
    )

    # calculate aggregated document rank score
    document_rank_score: dict[str, float] = {}
    for rank, page in enumerate(page_matches):
        document_rank_score[page.document_id] = document_rank_score.get(page.document_id, 0) + 1.0 / (rank + max_results / 2)

    document_rank_score = dict(sorted(document_rank_score.items(), key=lambda item: item[1], reverse=True))

    # now construct the document matches in rank order
    results = [
        DocumentSearchResult(
            id=document_id,
            page_matches=[p for p in page_matches if p.document_id == document_id],
        )
        for document_id in document_rank_score
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
                # page_number is expected to be available after loading pages
                def _page_num_key(x: DocumentPageSearchResult) -> int:
                    return x.page_number if x.page_number is not None else -1

                r.page_matches.sort(key=_page_num_key)

        # apply recency weight
        results = rerank_by_recency(results, recency_weight=recency_weight)

    # pull exact matches to the top
    if promote_exact_match and query:
        results = promote_exact_matches(query, results)

    # record rank
    for rank, result in enumerate(results):
        result.rank = rank + 1

    return results


#################################################
def hybrid_search(
    resource: APIResource,
    query: str,
    extended_search: bool = False,
    taxonomy_filters: List[TaxonomyFilter] | None = None,
) -> List[HybridSearchResult]:
    """
    Searches for documents using hybrid search combining text and vector search.

    Args:
        resource (APIResource): An instance of the DeepSights API resource.
        query (str): The search query.
        extended_search (bool, optional): Whether to perform extended search. Defaults to False.
        taxonomy_filters (List[TaxonomyFilter], optional): Taxonomy filters to apply. Defaults to None.

    Returns:
        List[HybridSearchResult]: The list of hybrid search results.
    """
    max_query_length = 512

    # Input validation
    if query is None:
        raise ValueError("The 'query' argument is required.")
    if not isinstance(query, str):
        raise ValueError("The 'query' must be a string.")
    query = query.strip()
    if len(query) == 0:
        raise ValueError("The 'query' cannot be empty.")
    if len(query) > max_query_length:
        raise ValueError(f"The 'query' must be {max_query_length} characters or less.")

    body: dict = {
        "query": query,
        "extended_search": extended_search,
    }

    # Add taxonomy filters if provided
    if taxonomy_filters:
        body["taxonomy_filters"] = [{"field": tf.field, "values": tf.values} for tf in taxonomy_filters]

    response = resource.api.post("supercharged-search-service/hybrid-searches", body=body)

    # Extract the search results from the response; a degraded backend may return
    # HTTP 200 with "context": null or "search_results": null, treat both as empty
    search_results = (response.get("context") or {}).get("search_results") or []
    return [HybridSearchResult(**result) for result in search_results]


#################################################
def topic_search(
    resource: APIResource,
    query: str,
    extended_search: bool = False,
    taxonomy_filters: List[TaxonomyFilter] | None = None,
    content_types: List[str] | None = None,
) -> List[TopicSearchResult]:
    """
    Searches for documents by topic using AI-powered analysis.

    Args:
        resource (APIResource): An instance of the DeepSights API resource.
        query (str): The search query topic.
        extended_search (bool, optional): Whether to perform extended search. Defaults to False.
        taxonomy_filters (List[TaxonomyFilter], optional): Taxonomy filters to apply. Defaults to None.
        content_types (List[str], optional): Artifact content types to filter by. Defaults to None.

    Returns:
        List[TopicSearchResult]: The list of topic search results.
    """
    # Input validation
    if not isinstance(query, str):
        raise ValueError("The 'query' must be a string.")
    query = query.strip()
    if len(query) == 0:
        raise ValueError("The 'query' cannot be empty.")
    if len(query) > 512:
        raise ValueError("The 'query' must be 512 characters or less.")

    body: dict = {
        "query": query,
        "extended_search": extended_search,
    }

    # Add taxonomy filters if provided
    if taxonomy_filters:
        body["taxonomy_filters"] = [{"field": tf.field, "values": tf.values} for tf in taxonomy_filters]

    # Add content type filter if provided
    if content_types:
        body["content_type_filter"] = {"content_types": content_types}

    response = resource.api.post("supercharged-search-service/topic-searches", body=body)

    # Extract the search results from the response; a degraded backend may return
    # HTTP 200 with "context": null or "search_results": null, treat both as empty
    search_results = (response.get("context") or {}).get("search_results") or []
    return [TopicSearchResult(**result) for result in search_results if result]


#################################################
# pylint: disable-next=too-many-arguments, too-many-positional-arguments, too-many-locals, too-many-branches
def text_search(
    resource: APIResource,
    metadata_query: Optional[str] = None,
    metadata_fields: Optional[List[str]] = None,
    content_query: Optional[str] = None,
    includes: Optional[List[str]] = None,
    excludes: Optional[List[str]] = None,
    content_types: Optional[List[str]] = None,
    taxonomy_filters: Optional[List[TaxonomyFilter]] = None,
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    limit: int = 10,
    sort_by: str = "RELEVANCY",
) -> List[TextSearchResult]:
    """
    Searches indexed artifacts by lexical text search.

    Unlike topic or hybrid search, this is a plain text search with no AI relevance
    judgment: results are scored by lexical relevancy (or recency) and carry highlights
    explaining where the query matched. Use it to locate documents by name, title,
    file name, or literal content — e.g. finding a specific (or older) edition of a
    named report that semantic search would rank away.

    Args:

        resource (APIResource): An instance of the DeepSights API resource.
        metadata_query (str, optional): Search query applied to the metadata fields.
        metadata_fields (List[str], optional): Metadata fields to search; any of
            'title', 'file_name', 'source', 'summary'. Defaults to ['title', 'file_name']
            when a metadata_query is given.
        content_query (str, optional): Search query applied to the content of indexed artifacts.
        includes (List[str], optional): Keywords that found documents must include.
        excludes (List[str], optional): Keywords that found documents must not include.
        content_types (List[str], optional): Artifact content types to filter by.
        taxonomy_filters (List[TaxonomyFilter], optional): Taxonomy filters to apply.
        from_date (datetime, optional): Only return artifacts published on or after this date.
        to_date (datetime, optional): Only return artifacts published on or before this date.
        limit (int, optional): The maximum number of results to return (1-100). Defaults to 10.
        sort_by (str, optional): 'RELEVANCY' or 'RECENCY'. Defaults to 'RELEVANCY'.

    Returns:

        List[TextSearchResult]: The list of text search results with scores and highlights.
    """
    # Input validation
    metadata_query = metadata_query.strip() if metadata_query else None
    content_query = content_query.strip() if content_query else None
    if not metadata_query and not content_query:
        raise ValueError("At least one of 'metadata_query' or 'content_query' is required.")
    for name, query in (("metadata_query", metadata_query), ("content_query", content_query)):
        if query is not None and len(query) > MAX_TEXT_SEARCH_QUERY_LENGTH:
            raise ValueError(f"The '{name}' must be {MAX_TEXT_SEARCH_QUERY_LENGTH} characters or less.")
    if metadata_fields is not None:
        invalid_fields = [field for field in metadata_fields if field not in TEXT_SEARCH_METADATA_FIELDS]
        if invalid_fields:
            raise ValueError(f"Invalid metadata fields {invalid_fields}; supported: {list(TEXT_SEARCH_METADATA_FIELDS)}.")
    if not 0 < limit <= 100:
        raise ValueError("The 'limit' must be between 1 and 100.")
    if sort_by not in TEXT_SEARCH_SORT_OPTIONS:
        raise ValueError(f"The 'sort_by' must be one of {list(TEXT_SEARCH_SORT_OPTIONS)}.")

    body: dict = {
        "limit": limit,
        "sort_by": sort_by,
    }
    if metadata_query:
        body["metadata_query"] = metadata_query
        body["metadata_fields_to_search"] = metadata_fields if metadata_fields is not None else ["title", "file_name"]
    if content_query:
        body["content_query"] = content_query
    if includes:
        body["includes"] = includes
    if excludes:
        body["excludes"] = excludes
    if content_types:
        body["content_type_filter"] = {"content_types": content_types}
    if taxonomy_filters:
        body["taxonomy_filters"] = [{"field": tf.field, "values": tf.values} for tf in taxonomy_filters]
    if from_date or to_date:
        date_filter = {}
        if from_date:
            date_filter["from"] = from_date.isoformat()
        if to_date:
            date_filter["to"] = to_date.isoformat()
        body["publication_date_filter"] = date_filter

    response = resource.api.post("end-user-gateway-service/text-searches/_search", body=body)

    results = [TextSearchResult(**result) for result in response.get("results") or []]

    # record rank
    for rank, result in enumerate(results):
        result.rank = rank + 1

    return results
