import json
import deepsights

# get the test embedding from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    test_embedding = json.load(f)["embedding"]


def test_document_pages_search_plain():
    results = deepsights.document_pages_search(
        deepsights.DeepSights(),
        test_embedding,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.document_id is not None
        assert result.id is not None
        assert result.score > 0

        if ix > 0:
            assert result.score <= results[ix - 1].score


def test_document_pages_search_cutoff():
    results = deepsights.document_pages_search(
        deepsights.DeepSights(), test_embedding, min_score=0.9999
    )

    assert len(results) == 0


def test_document_pages_search_with_loading():
    results = deepsights.document_pages_search(
        deepsights.DeepSights(),
        test_embedding,
        max_results=10,
        load_pages=True,
    )

    assert len(results) == 10
    for ix, result in enumerate(results):
        assert result.document_id is not None
        assert result.id is not None
        assert result.score > 0
        assert result.text is not None
        assert result.page_number is not None

        if ix > 0:
            assert result.score <= results[ix - 1].score


def test_documents_search_plain():
    results = deepsights.documents_search(
        deepsights.DeepSights(),
        query_embedding=test_embedding,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.document is None
        assert result.page_matches is not None
        assert len(result.page_matches) > 0
        for page in result.page_matches:
            assert page.id is not None
        assert result.score_rank == ix + 1
        assert result.age_rank is None
        assert result.rank == result.score_rank


def test_documents_search_with_recency_low():
    results = deepsights.documents_search(
        deepsights.DeepSights(),
        query_embedding=test_embedding,
        max_results=10,
        recency_weight=0.00001,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.document is not None
        assert result.page_matches is not None
        assert len(result.page_matches) > 0
        for page in result.page_matches:
            assert page.id is not None
        assert result.rank == ix + 1
        assert result.score_rank == result.rank
        assert result.age_rank is not None


def test_documents_search_with_recency_high():
    results = deepsights.documents_search(
        deepsights.DeepSights(),
        query_embedding=test_embedding,
        max_results=10,
        recency_weight=0.99999,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.document is not None
        assert result.page_matches is not None
        assert len(result.page_matches) > 0
        for page in result.page_matches:
            assert page.id is not None
        assert result.rank == ix + 1
        assert result.score_rank is not None
        assert result.age_rank == result.rank


def test_documents_search_with_loading():
    results = deepsights.documents_search(
        deepsights.DeepSights(),
        query_embedding=test_embedding,
        max_results=10,
        load_documents=True,
    )

    assert len(results) > 0
    for ix, result in enumerate(results):
        assert result.id is not None
        assert result.document is not None
        assert result.page_matches is not None
        assert len(result.page_matches) > 0
        for page in result.page_matches:
            assert page.id is not None
            assert page.text is not None
        assert result.score_rank == ix + 1
        assert result.age_rank is None
        assert result.rank == result.score_rank
