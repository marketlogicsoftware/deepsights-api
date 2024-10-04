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
This module contains the functions to load documents from the DeepSights API.
"""

from typing import List
from deepsights.api import APIResource
from deepsights.utils import run_in_parallel
from deepsights.documentstore.resources.documents._cache import (
    get_document,
    get_document_cache_size,
    has_document,
    set_document,
    get_document_page,
    get_document_page_cache_size,
    has_document_page,
    set_document_page,
)
from deepsights.documentstore.resources.documents._model import Document, DocumentPage
from deepsights.documentstore.resources.documents._segmenter import segment_landscape_page


#################################################
def document_pages_load(resource: APIResource, page_ids: List[str]):
    """
    Load document pages from the cache or fetch them from the API if not cached.

    Args:

        resource (APIResource): An instance of the DeepSights API resource.
        page_ids (List[str]): A list of page IDs to load.

    Returns:

        List[DocumentPage]: A list of loaded document pages.
    """

    assert (
        len(page_ids) < get_document_page_cache_size()
    ), "Cannot load more document pages than the cache size."

    # touch cached document pages
    for page_id in page_ids:
        get_document_page(page_id)

    # filter uncached document pages
    uncached_document_page_ids = [
        page_id for page_id in page_ids if not has_document_page(page_id)
    ]

    # load uncached document pages
    def _load_document_page(page_id: str):
        result = resource.api.get(f"/artifact-service/pages/{page_id}", timeout=5)

        # map the document page
        return DocumentPage(
            id=result["id"],
            page_number=result["number"],
            text=segment_landscape_page(result),
        )

    uncached_document_pages = run_in_parallel(
        _load_document_page, uncached_document_page_ids, max_workers=5
    )

    # set in cache
    for page in uncached_document_pages:
        set_document_page(page.id, page)

    # collect results
    return [get_document_page(page_id) for page_id in page_ids]


#################################################
def documents_load(
    resource: APIResource,
    document_ids: List[str],
    force_load: bool = False,
    load_pages: bool = False,
):
    """
    Load documents from the DeepSights API.

    Args:

        resource (APIResource): An instance of the DeepSights API resource.
        document_ids (List[str]): A list of document IDs to load.
        force_load (bool, optional): Whether to force load the documents, even if in cache. Defaults to False.
        load_pages (bool, optional): Whether to load the pages of the documents. Defaults to False.

    Returns:

        List[Document]: A list of loaded documents.
    """
    assert (
        len(document_ids) < get_document_cache_size()
    ), "Cannot load more documents than the cache size."

    # Identify documents that need loading or page loading
    docs_to_load = []
    docs_to_load_pages = []

    for doc_id in document_ids:
        if force_load or not has_document(doc_id):
            docs_to_load.append(doc_id)
        elif load_pages and not get_document(doc_id).page_ids:
            docs_to_load_pages.append(doc_id)

    # Load uncached documents
    def _load_document(document_id: str):
        result = resource.api.get(
            f"/artifact-service/artifacts/{document_id}", timeout=5
        )

        # capitalize the first letter of the summary
        result["summary"] = result["summary"][0].upper() + result["summary"][1:]

        # map the document
        return Document.model_validate(result)

    newly_loaded_docs = run_in_parallel(
        _load_document, docs_to_load, max_workers=5
    )

    # Load pages if requested
    if load_pages:
        all_docs_needing_pages = newly_loaded_docs + [get_document(doc_id) for doc_id in docs_to_load_pages]
        
        def _load_pages(document: Document):
            if not document.page_ids:
                result = resource.api.get(
                    f"/artifact-service/artifacts/{document.id}/page-ids", timeout=5
                )
                document.page_ids = result["ids"]
            return document.page_ids

        all_page_ids = run_in_parallel(
            _load_pages, all_docs_needing_pages, max_workers=5
        )

        # Flatten page ids
        flat_page_ids = [page_id for page_ids in all_page_ids for page_id in page_ids]

        # Load actual pages
        document_pages_load(resource, flat_page_ids)

    # Update cache with newly loaded documents and documents with newly loaded pages
    for doc in newly_loaded_docs:
        set_document(doc.id, doc)
    for doc_id in docs_to_load_pages:
        set_document(doc_id, get_document(doc_id))

    # Collect results
    return [get_document(doc_id) for doc_id in document_ids]