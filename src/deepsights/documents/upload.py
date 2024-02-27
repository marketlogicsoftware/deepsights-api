import os
import time
import requests
from deepsights import DeepSights
from deepsights.documents.load import documents_load


def document_upload(api: DeepSights, document_filename: str):
    """
    Upload a document to the DeepSights API.

    Args:
        document_filename (str): The filename of the document to upload. Must be PDF, PPT(X), DOC(X)
    """
    # check if document exists
    if not os.path.exists(document_filename):
        raise FileNotFoundError(f"Document {document_filename} does not exist.")

    # check proper file extension: must be PDF, PPT, PPTX, DOC, DOCX
    if not document_filename.lower().endswith(
        (".pdf", ".ppt", ".pptx", ".doc", ".docx")
    ):
        raise ValueError(
            f"Document {document_filename} is not a valid file type. Only supporting PDF, PPT, PPTX, DOC, DOCX."
        )

    # get file basename
    document_basename = os.path.basename(document_filename)

    # obtain upload link
    response = api.post(
        "/artifact-service/document-upload-links/_generate",
        body={
            "file_name": document_basename,
            "file_type": document_filename.split(".")[-1].upper(),
        },
    )
    upload_link = response["signed_link"]
    gcs_object_id = response["gcs_object_id"]

    # upload document
    with open(document_filename, "rb") as f:
        headers = {
            "Content-Type": document_filename.split(".")[-1].upper(),
            "x-goog-if-generation-match": 0,
        }
        response = requests.put(upload_link, headers=headers, data=f, timeout=30)

    # check response
    if response.status_code != 200:
        raise ValueError(
            f"Document {document_filename} failed to upload: {response.text}"
        )

    # create artifact
    response = api.post(
        "/artifact-service/artifacts",
        body={"gcs_object_id": gcs_object_id},
    )

    # return artifact ID
    return response["id"]


def document_wait_for_processing(api: DeepSights, document_id: str):
    """
    Wait for the document to be processed and completed.

    Args:
        document_id (str): The ID of the document to wait for.
    """
    # wait for completion
    while True:
        response = api.get(f"/artifact-service/artifacts/{document_id}")
        if response["status"] == "COMPLETED":
            break
        elif response["status"].startswith("FAILED"):
            raise ValueError(
                f"Document {document_id} failed to process: {response['error_message']}"
            )
        else:
            time.sleep(2)

    # now load into cache
    documents_load(api, [document_id])
