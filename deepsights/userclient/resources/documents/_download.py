"""
This module contains the functions to download documents via the end-user gateway.
"""

import os
import tempfile
import urllib.parse
import urllib.request

from deepsights.api import APIResource


#################################################
def document_download(
    resource: APIResource,
    document_id: str,
    output_dir: str,
    force_download: bool = False,
) -> str:
    """
    Download a document via the end-user gateway.

    Args:
        resource (APIResource): An instance of the DeepSights API resource.
        document_id (str): The ID of the document to download.
        output_dir (str): The local directory to save the downloaded document in.
        force_download (bool): If True, the document will be downloaded even if it already exists locally.

    Raises:
        FileNotFoundError: If the local directory does not exist.
        ValueError: If the document fails to download or link is invalid.

    Returns:
        str: The local path of the downloaded document.
    """
    # check if local path exists
    if not os.path.exists(output_dir):
        raise FileNotFoundError(f"Local directory {output_dir} does not exist.")

    # obtain real filename (and validate existence via API)
    # local import to avoid circular import at module load time
    from deepsights.userclient.resources.documents.documents import (  # pylint: disable=import-outside-toplevel
        documents_load,
    )

    document = documents_load(resource, [document_id])[0]
    # Sanitize filename to prevent path traversal attacks
    safe_filename = os.path.basename(document.file_name or "unknown")
    local_filename = os.path.join(output_dir, f"{document.id}-{safe_filename}")

    # already downloaded?
    if force_download or not os.path.exists(local_filename):
        # obtain download link from end-user gateway
        response = resource.api.get(
            f"/end-user-gateway-service/artifacts/{document_id}/gcs-object-link",
        )

        # download via secure temp file to prevent partial downloads and race conditions
        with tempfile.NamedTemporaryFile(dir=output_dir, delete=False) as temp_file:
            temp_filename = temp_file.name

        # Validate URL scheme to prevent using local file paths or unexpected protocols
        parsed_url = urllib.parse.urlparse(response["signed_link"])
        if parsed_url.scheme not in ("http", "https"):
            raise ValueError(f"Unsupported URL scheme '{parsed_url.scheme}' in signed link.")

        # The scheme has been validated; the call is considered safe.
        urllib.request.urlretrieve(  # nosec B310
            response["signed_link"], temp_filename
        )
        os.rename(temp_filename, local_filename)

    # return the filename
    return local_filename
