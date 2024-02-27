import time
import requests
from typing import List
from deepsights import DeepSights
from deepsights.documents._cache import remove_document


def documents_delete(api: DeepSights, document_ids: List):
    """
    Delete documents from the DeepSights API.

    Args:
        api (DeepSights): An instance of the DeepSights API client.
        document_ids (List): A list of document IDs to be deleted.

    Returns:
        None
    """

    # delete documents one by one
    for document_id in document_ids:
        api.delete(
            f"/artifact-service/artifacts/{document_id}",
        )

        # remove from cache
        remove_document(document_id)


def document_wait_for_deletion(api: DeepSights, document_id: str):
    """
    Wait for the document to be deleted.

    Args:
        document_id (str): The ID of the document to wait for.
    """
    # wait for completion
    while True:
        try:
            response = api.get(f"/artifact-service/artifacts/{document_id}")
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return
            else:
                raise e

        if response["status"] in ("DELETING", "SCHEDULED_FOR_DELETING"):
            time.sleep(2)
        elif response["status"].startswith("FAILED"):
            raise ValueError(
                f"Document {document_id} failed to delete: {response['error_message']}"
            )
