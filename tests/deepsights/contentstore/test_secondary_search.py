import json
import pytest
import deepsights
from deepsights.contentstore.secondary import _secondary_text_search, _secondary_vector_search


# get the test data from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    data = json.load(f)
    test_embedding = data["embedding"]
    test_query = data["question"]


    results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=5,
    )

    assert len(results) == 5
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.source is not None

        if ix > 0:
            assert result.rank > results[ix - 1].rank


def test_secondary_text_search_with_recency_low():
    results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=10,
        recency_weight=0.00001,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1
        assert result.score_rank == result.rank
        assert result.age_rank is not None


def test_secondary_text_search_with_recency_high():
    results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=10,
        recency_weight=0.99999,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1
        assert result.score_rank is not None
        assert result.age_rank == result.rank


def test_secondary_vector_search():
    results = _secondary_vector_search(
        deepsights.ContentStore(),
        test_embedding,
        max_results=5,
    )

    assert len(results) == 5
    for ix, result in enumerate(results):
        assert result.id is not None

        if ix > 0:
            assert result.rank > results[ix - 1].rank


def test_secondary_vector_search_with_recency_low():
    results = _secondary_vector_search(
        deepsights.ContentStore(),
        test_embedding,
        max_results=10,
        recency_weight=0.00001,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1
        assert result.score_rank == result.rank
        assert result.age_rank is not None


def test_secondary_vector_search_with_recency_high():
    results = _secondary_vector_search(
        deepsights.ContentStore(),
        test_embedding,
        max_results=10,
        recency_weight=0.99999,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.rank == ix + 1
        assert result.score_rank is not None
        assert result.age_rank == result.rank


def test_secondary_hybrid_search_fail():
    with pytest.raises(ValueError):
        deepsights.secondary_search(
            deepsights.ContentStore(),
            max_results=5,
        )


def test_secondary_hybrid_search_only_vector():
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        max_results=5,
    )

    vector_results = _secondary_vector_search(
        deepsights.ContentStore(),
        test_embedding,
        max_results=5,
    )

    assert len(hybrid_results) == 5
    for ix, hybrid_result in enumerate(hybrid_results):
        assert hybrid_result == vector_results[ix]


def test_secondary_hybrid_search_only_text():
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=5,
    )

    text_results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=5,
    )

    assert len(hybrid_results) == 5
    for ix, hybrid_result in enumerate(hybrid_results):
        assert hybrid_result == text_results[ix]


def test_secondary_hybrid_search():
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        query=test_query,
        max_results=10,
    )

    vector_results = _secondary_vector_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        max_results=10,
    )

    text_results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=10,
    )

    assert len(hybrid_results) == 10

    hybrid_ids = [result.id for result in hybrid_results]

    contrib_ids = [result.id for result in vector_results]
    contrib_ids += [result.id for result in text_results]

    assert all([result in contrib_ids for result in hybrid_ids])


def test_secondary_hybrid_search_with_vector_high():
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        query=test_query,
        max_results=10,
        vector_weight=0.99999,
    )

    vector_results = _secondary_vector_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        max_results=10,
    )

    assert len(hybrid_results) == 10
    for ix, result in enumerate(hybrid_results):
        assert result.id == vector_results[ix].id


def test_secondary_hybrid_search_with_vector_low():
    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query_embedding=test_embedding,
        query=test_query,
        max_results=10,
        vector_weight=0.00001,
    )

    text_results = _secondary_text_search(
        deepsights.ContentStore(),
        query=test_query,
        max_results=10,
    )

    assert len(hybrid_results) == 10
    for ix, result in enumerate(hybrid_results):
        assert result.id == text_results[ix].id


def test_secondary_text_search_with_title_promotion():
    query = "gen x video viewers"

    hybrid_results_no_promotion = deepsights.secondary_search(
        deepsights.ContentStore(),
        query=query,
        max_results=10,
        promote_exact_match=False,
        recency_weight=0.9,
    )

    hybrid_results = deepsights.secondary_search(
        deepsights.ContentStore(),
        query=query,
        max_results=10,
        promote_exact_match=True,
        recency_weight=0.9,
    )

    assert hybrid_results[0].id != hybrid_results_no_promotion[0].id
    assert all([term in hybrid_results[0].title.lower() for term in query.split()])
    assert not all(
        [term in hybrid_results_no_promotion[0].title.lower() for term in query.split()]
    )
