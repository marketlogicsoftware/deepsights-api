from typing import List
from deepsights.api import DeepSights
from deepsights.utils import rerank_by_recency, promote_exact_matches
from deepsights.documents._cache import get_document, get_document_page
from deepsights.documents._model import DocumentPageSearchResult, DocumentSearchResult
from deepsights.documents.load import documents_load, document_pages_load


#################################################
def document_pages_search(
    api: DeepSights,
    query_embedding: List,
    min_score: float = 0.7,
    max_results: int = 50,
    load_pages=False,
):
    """
    Searches for document pages based on their vector embeddings.

    Args:
        api (ds.DeepSights): The DeepSights API instance.
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
    response = api.post(
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
        document_pages_load(api, page_ids=[r.id for r in results])

        # reference the pages
        for r in results:
            r.page = get_document_page(r.id)

    return results


#################################################
def documents_search(
    api: DeepSights,
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
        api (ds.DeepSights): The DeepSights API instance.
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
        api,
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
            score_rank=rank + 1,
            pages=[p for p in page_matches if p.document_id == document_id],
        )
        for rank, document_id in enumerate(document_rank_score)
    ]

    # load documents if requested
    if load_documents or recency_weight:
        # make sure the documents are loaded
        documents_load(api, document_ids=[r.id for r in results])

        # reference the documents & set timestamp
        for r in results:
            r.document = get_document(r.id)
            r.timestamp = r.document.timestamp

        # apply recency weight
        results = rerank_by_recency(results, recency_weight=recency_weight)

    # pull exact matches to the top
    if promote_exact_match and query:
        results = promote_exact_matches(query, results)

    # record rank
    for rank, result in enumerate(results):
        result.rank = rank + 1

    return results
