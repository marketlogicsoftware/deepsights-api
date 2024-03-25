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
This module contains the functions to delete documents from the DeepSights API.
"""

import time
from typing import List
import requests
from deepsights.api import APIResource
from deepsights.documentstore.resources.documents._cache import remove_document


#################################################
def documents_delete(resource: APIResource, document_ids: List):
    """
    Delete documents from the DeepSights API.

    Args:

        resource (APIResource): An instance of the DeepSights API resource.
        document_ids (List): A list of document IDs to be deleted.
    """

    # delete documents one by one
    for document_id in document_ids:
        resource.api.delete(
            f"/artifact-service/artifacts/{document_id}",
        )

        # remove from cache
        remove_document(document_id)


#################################################
def document_wait_for_deletion(
    resource: APIResource, document_id: str, timeout: int = 60
):
    """
    Wait for the document to be deleted.

    Args:

        resource (APIResource): An instance of the DeepSights API resource.
        document_id (str): The ID of the document to wait for.
        timeout (int, optional): The maximum time to wait for the document to be deleted, in seconds. Defaults to 60.

    Raises:

        TimeoutError: If the document fails to delete within the specified timeout.
        ValueError: If the document deletion fails with an error message.
    """
    # wait for completion
    start = time.time()
    while time.time() - start < timeout:
        try:
            response = resource.api.get(f"/artifact-service/artifacts/{document_id}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                remove_document(document_id)
                return

            raise e

        if response["status"] in ("DELETING", "SCHEDULED_FOR_DELETING"):
            time.sleep(2)
        elif response["status"].startswith("FAILED"):
            raise ValueError(
                f"Document {document_id} failed to delete: {response['error_message']}"
            )

    raise TimeoutError(f"Document {document_id} failed to delete in {timeout} seconds.")
