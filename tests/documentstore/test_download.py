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
Test the documents_download function
"""

import os
import tempfile
from typing import Any

import pytest
import requests

import deepsights


def test_document_download_404(ds_client: deepsights.DeepSights):
    """
    Test case for document download with a non-existing document ID.
    It verifies that the function raises an HTTPError with a status code of 404.
    """
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        ds_client.documentstore.documents.download(
            "non_existing_document_id",
            tempfile.gettempdir(),
        )

    assert exc.value.response.status_code == 404


def test_document_download_no_path(ds_client: deepsights.DeepSights):
    """
    Test case to verify that a FileNotFoundError is raised when attempting to download a document
    with a non-existing path.
    """
    with pytest.raises(FileNotFoundError):
        ds_client.documentstore.documents.download(
            "non_existing_document_id",
            "/does_not_exist",
        )


def test_document_download(ds_client: deepsights.DeepSights, test_data: Any):
    """
    Test case for the document_download function.

    This function tests the functionality of the document_download function by downloading a document
    using a DeepSights instance and verifying the existence of the downloaded file.

    """
    local_filename = ds_client.documentstore.documents.download(
        test_data["document_id"],
        tempfile.gettempdir(),
    )

    assert os.path.exists(local_filename)

    os.remove(local_filename)
