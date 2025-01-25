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
This module contains the base functions to download content from the ContentStore.
"""

import os
import tempfile
import urllib.request

from deepsights.api import APIResource


#################################################
def contentstore_download(resource: APIResource, item_id: str) -> str:
    """
    Downloads and returns the extracted text content of an item from the ContentStore.

    This function retrieves a signed download link for the specified item's extracted text content
    from the ContentStore API, downloads the content to a temporary file, reads the text content,
    and returns it as a string. The temporary file is automatically cleaned up after use.

    Args:
        resource (APIResource): An instance of the DeepSights API resource used to make API calls
            to the ContentStore service.
        item_id (str): The unique identifier of the item whose content should be downloaded.

    Raises:
        ValueError: If the download fails for any reason, such as network errors, invalid item ID,
            or issues reading the downloaded content.

    Returns:
        str: The extracted text content of the downloaded item as a string.
    """
    return str(
        resource.api.get_content(
            f"/item-service/items/{item_id}/_download-content-extracted-text",
        )
    )
