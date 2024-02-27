import json
import pytest
import requests
import deepsights

# get the test embedding from JSON
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    test_data = json.load(f)
    test_document_id = test_data["document_id"]
    test_page_id = test_data["document_page_id"]


def test_document_load_404():
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        deepsights.documents_load(
            deepsights.DeepSights(),
            ["aaa"],
            load_pages=False,
        )

    assert exc.value.response.status_code == 404


def test_document_load():
    deepsights.set_document(test_document_id, None)

    documents = deepsights.documents_load(
        deepsights.DeepSights(),
        [test_document_id],
        load_pages=False,
    )

    assert len(documents) == 1
    assert documents[0].id == test_document_id
    assert documents[0].status is not None
    assert documents[0].title is not None
    assert documents[0].file_name is not None
    assert documents[0].file_size > 0
    assert documents[0].description is not None
    assert documents[0].timestamp is not None
    assert documents[0].page_ids is None
    assert documents[0].number_of_pages > 0

    assert deepsights.has_document(test_document_id)

    # test caching
    documents[0].title = "__TEST__"
    documents = deepsights.documents_load(
        deepsights.DeepSights(),
        [test_document_id],
        load_pages=False,
    )
    assert documents[0].title == "__TEST__"


def test_document_load_with_pages():
    deepsights.set_document(test_document_id, None)

    documents = deepsights.documents_load(
        deepsights.DeepSights(),
        [test_document_id],
        load_pages=True,
    )

    assert len(documents) == 1
    assert documents[0].id == test_document_id
    assert documents[0].status is not None
    assert documents[0].title is not None
    assert documents[0].file_name is not None
    assert documents[0].file_size > 0
    assert documents[0].description is not None
    assert documents[0].timestamp is not None
    assert len(documents[0].page_ids) > 0
    assert documents[0].number_of_pages > 0

    assert deepsights.has_document(test_document_id)
    for page_id in documents[0].page_ids:
        assert deepsights.has_document_page(page_id)


def test_document_page_load():
    deepsights.set_document_page(test_page_id, None)

    pages = deepsights.document_pages_load(deepsights.DeepSights(), [test_page_id])

    assert len(pages) == 1
    assert pages[0].id == test_page_id
    assert pages[0].page_number > 0
    assert pages[0].text is not None

    assert deepsights.has_document_page(test_page_id)
