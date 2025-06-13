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
This module contains the functions to download documents to the DeepSights API.
"""

import os
import tempfile
import urllib.parse
import urllib.request

from deepsights.api import APIResource
from deepsights.documentstore.resources.documents._load import documents_load


#################################################
def document_download(
    resource: APIResource,
    document_id: str,
    output_dir: str,
    force_download: bool = False,
) -> str:
    """
    Download a document from the DeepSights API.

    Args:
        resource (APIResource): An instance of the DeepSights API resource.
        document_id (str): The ID of the document to download.
        output_dir (str): The local directory to save the downloaded document in.
        force_download (bool): If True, the document will be downloaded even if it already exists locally.

    Raises:
        FileNotFoundError: If the local directory does not exist.
        ValueError: If the document fails to download.

    Returns:
        str: The local path of the downloaded document.
    """
    # check if local path exists
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Local directory {output_dir} does not exist.")

    # obtain real filename
    document = documents_load(resource, [document_id])[0]
    # Sanitize filename to prevent path traversal attacks
    safe_filename = os.path.basename(document.file_name or "unknown")
    local_filename = os.path.join(output_dir, f"{document.id}-{safe_filename}")

    # already downloaded?
    if force_download or not os.path.exists(local_filename):
        # obtain download link
        response = resource.api.get(
            f"/artifact-service/artifacts/{document_id}/gcs-object-link",
        )

        # download via secure temp file to prevent partial downloads and race conditions
        with tempfile.NamedTemporaryFile(dir=output_dir, delete=False) as temp_file:
            temp_filename = temp_file.name

        # Validate URL scheme to prevent using local file paths or unexpected protocols
        parsed_url = urllib.parse.urlparse(response["signed_link"])
        if parsed_url.scheme not in ("http", "https"):
            raise ValueError(
                f"Unsupported URL scheme '{parsed_url.scheme}' in signed link."
            )

        # The scheme has been validated; the call is considered safe.
        urllib.request.urlretrieve(  # nosec B310
            response["signed_link"], temp_filename
        )
        os.rename(temp_filename, local_filename)

    # return the filename
    return local_filename
