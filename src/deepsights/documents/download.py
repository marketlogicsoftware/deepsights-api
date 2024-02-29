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
This module contains the functions to download documents to the DeepSights API.
"""

import os
import urllib.request
import tempfile
from deepsights.api import DeepSights
from deepsights.documents.load import documents_load


#################################################
def document_download(api: DeepSights, document_id: str, local_path: str):
    """
    Download a document from the DeepSights API.

    Args:

        api (DeepSights): An instance of the DeepSights API client.
        document_id (str): The ID of the document to download.
        local_path (str): The local path to save the downloaded document in.

    Raises:

        FileNotFoundError: If the local directory does not exist.
        ValueError: If the document fails to download.

    Returns:

        Tuple[str, str]: A tuple containing the file name and the local path of the downloaded document.
    """
    # check if local path exists
    if not os.path.exists(local_path):
        raise FileNotFoundError(f"Local directory {local_path} does not exist.")

    # obtain real filename
    document = documents_load(api, [document_id])[0]

    # obtain download link
    response = api.get(
        f"/artifact-service/artifacts/{document_id}/gcs-object-link",
    )

    # download document to temp file
    local_filename = tempfile.mktemp(dir=local_path)
    urllib.request.urlretrieve(response["signed_link"], local_filename)

    # return the filename
    return document.file_name, local_filename
