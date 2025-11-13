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
Tests for userclient documents download
"""

import os
import tempfile
from typing import Any

import pytest
import requests


def test_document_download_404(user_client):
    """Ensure downloading a non-existent document raises HTTPError (404)."""
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        user_client.documents.download(
            "non_existing_document_id",
            tempfile.gettempdir(),
        )

    assert exc.value.response.status_code == 404


def test_document_download_no_path(user_client):
    """Ensure downloading to a non-existent directory raises FileNotFoundError."""
    with pytest.raises(FileNotFoundError):
        user_client.documents.download(
            "non_existing_document_id",
            "/does_not_exist",
        )


def test_document_download(user_client, test_data: Any):
    """Happy path: download a real document and ensure the file exists, then clean up."""
    local_filename = user_client.documents.download(
        test_data["document_id"],
        tempfile.gettempdir(),
    )

    assert os.path.exists(local_filename)

    os.remove(local_filename)


pytestmark = pytest.mark.integration
