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
Test the lifecycle of documents
"""

import pytest
import requests
import deepsights


def test_documents_upload_no_file():
    """
    Test case to verify that a FileNotFoundError is raised when trying to upload a non-existing file.
    """
    with pytest.raises(FileNotFoundError):
        deepsights.document_upload(
            deepsights.DeepSights(),
            "tests/data/non_existing.pdf",
        )


def test_documents_upload_unsupported_type():
    """
    Test case to verify that uploading an unsupported file type raises a ValueError.
    """
    with pytest.raises(ValueError):
        deepsights.document_upload(
            deepsights.DeepSights(),
            "tests/data/test_text.txt",
        )


def test_documents_delete_404():
    """
    Test case for deleting documents with a 404 response.

    This test verifies that when attempting to delete documents that do not exist,
    a 404 response is returned.

    """
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        deepsights.documents_delete(
            deepsights.DeepSights(),
            ["aaa"],
        )

    assert exc.value.response.status_code == 404


def test_documents_upload_and_delete():
    """
    Test case for uploading and deleting documents.
    """
    # upload the document
    artifact_id = deepsights.document_upload(
        deepsights.DeepSights(),
        "tests/data/test_presentation.pdf",
    )

    assert artifact_id is not None

    # wait for completion
    deepsights.document_wait_for_processing(deepsights.DeepSights(), artifact_id)

    doc = deepsights.get_document(artifact_id)
    assert doc is not None
    assert doc.id == artifact_id
    assert doc.status == "COMPLETED"

    # delete
    deepsights.documents_delete(
        deepsights.DeepSights(),
        [artifact_id],
    )

    assert not deepsights.has_document(artifact_id)

    # check status
    try:
        doc = deepsights.documents_load(deepsights.DeepSights(), [artifact_id])[0]

        assert doc is not None
        assert doc.id == artifact_id
        assert doc.status in ("DELETING", "SCHEDULED_FOR_DELETING")
    except requests.exceptions.HTTPError as e:
        # already deleted
        assert e.response.status_code == 404

    # wait for deletion
    deepsights.document_wait_for_deletion(deepsights.DeepSights(), artifact_id)

    # assert gone
    with pytest.raises(requests.exceptions.HTTPError):
        docs = deepsights.documents_load(deepsights.DeepSights(), [artifact_id])
        print(docs)
