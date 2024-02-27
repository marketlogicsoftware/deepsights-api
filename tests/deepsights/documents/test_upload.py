import pytest
import requests
import deepsights


def test_documents_upload_no_file():
    with pytest.raises(FileNotFoundError):
        deepsights.document_upload(
            deepsights.DeepSights(),
            "tests/data/non_existing.pdf",
        )


def test_documents_upload_unsupported_type():
    with pytest.raises(ValueError):
        deepsights.document_upload(
            deepsights.DeepSights(),
            "tests/data/test_text.txt",
        )


def notest_documents_upload_and_delete():
    # upload the document
    id = deepsights.document_upload(
        deepsights.DeepSights(),
        "tests/data/test_presentation.pptx",
    )

    assert id is not None

    # wait for completion
    deepsights.document_wait_for_processing(deepsights.DeepSights(), id)

    doc = deepsights.get_document(id)
    assert doc is not None
    assert doc["id"] == id
    assert doc["status"] == "COMPLETED"

    # delete
    deepsights.documents_delete(
        deepsights.DeepSights(),
        [id],
    )

    assert not deepsights.has_document(id)

    # check status
    try:
        doc = deepsights.documents_load(deepsights.DeepSights(), [id])[0]

        assert doc is not None
        assert doc.document_id == id
        assert doc.status in ("DELETING", "SCHEDULED_FOR_DELETING")
    except requests.exceptions.HTTPError as e:
        # already deleted
        assert e.response.status_code == 404

    # wait for deletion
    deepsights.document_wait_for_deletion(deepsights.DeepSights(), id)

    # assert gone
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        deepsights.documents_load(deepsights.DeepSights(), [id])
