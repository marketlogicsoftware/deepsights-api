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
This module contains the functions to perform hybrid searches via the DeepSights API.
"""

from typing import List

from deepsights.api import APIResource
from deepsights.documentstore.resources.documents._cache import (
    get_document,
    get_document_cache_size,
    get_document_page,
    get_document_page_cache_size,
    has_document,
    has_document_page,
    set_document,
    set_document_page,
)
from deepsights.documentstore.resources.documents._model import (
    Document,
    DocumentPage,
    HybridSearchResult,
    SortingField,
    SortingOrder,
)
from deepsights.documentstore.resources.documents._segmenter import (
    segment_landscape_page,
)
from deepsights.utils import run_in_parallel


#################################################
class DocumentResource(APIResource):
    """
    Represents a resource for performing hybrid searches via the DeepSights API.
    """

    MAX_QUERY_LENGTH = 512

    #################################################
    def search(
        self, query: str, extended_search: bool = False
    ) -> List[HybridSearchResult]:
        """
        Searches for documents using hybrid search combining text and vector search.

        Args:
            query (str): The search query.
            extended_search (bool, optional): Whether to perform extended search. Defaults to False.

        Returns:
            List[HybridSearchResult]: The list of hybrid search results.
        """
        # Input validation
        if not isinstance(query, str):
            raise ValueError("The 'query' must be a string.")
        query = query.strip()
        if len(query) == 0:
            raise ValueError("The 'query' cannot be empty.")
        if len(query) > self.MAX_QUERY_LENGTH:
            raise ValueError(
                f"The 'query' must be {self.MAX_QUERY_LENGTH} characters or less."
            )

        body = {
            "query": query,
            "extended_search": extended_search,
        }

        # Temporarily allow 5xx responses to debug the error
        response = self.api.post("end-user-gateway-service/hybrid-searches", body=body)

        # Extract the search results from the response
        search_results = response.get("context", {}).get("search_results", [])
        return [HybridSearchResult(**result) for result in search_results]

    #################################################
    def documents_list(
        self,
        page_size: int = 50,
        page_number: int = 0,
        sort_order: str = SortingOrder.DESCENDING,
        sort_field: str = SortingField.CREATION_DATE,
        status_filter: List[str] = [],
    ):
        """
        List documents from the DeepSights API.

        Args:
            page_size (int): The number of pages to return.
            page_number (int): The page number to return.
            sort_order (str): The sorting order.
            sort_field (str): The sorting field.
            status_filter (str): The optional status filter.

        Returns:
            tuple: A tuple containing the total number of results and the list of documents
        """
        assert page_size <= 100, "The page size must be less than or equal to 100."
        assert page_number >= 0, "The page number must be greater than 0."
        assert sort_order in [
            SortingOrder.ASCENDING,
            SortingOrder.DESCENDING,
        ], "The sort order must be 'ASC' or 'DESC'."
        assert sort_field in [
            SortingField.TITLE,
            SortingField.PUBLICATION_DATE,
            SortingField.CREATION_DATE,
        ], (
            "The sort field must be 'title', 'publication_date', or 'origin.creation_time'."
        )

        # construct
        body = {
            "size": page_size,
            "page": page_number,
            "sorting": {"field_name": sort_field, "sorting_direction": sort_order},
        }
        if status_filter:
            body["statuses"] = status_filter

        # fetch ids
        result = self.api.post(
            "/end-user-gateway-service/artifacts/_search",
            body=body,
        )

        # get results
        total_results = result["total_items"]
        documents = [Document.model_validate(result) for result in result["items"]]

        # set documents
        for document in documents:
            set_document(document.id, document)

        return total_results, documents

    #################################################
    def document_pages_load(self, page_ids: List[str]) -> List[DocumentPage]:
        """
        Load document pages from the cache or fetch them from the API if not cached.

        Args:
            page_ids (List[str]): A list of page IDs to load.

        Returns:
            List[DocumentPage]: A list of loaded document pages.
        """
        assert len(page_ids) < get_document_page_cache_size(), (
            "Cannot load more document pages than the cache size."
        )

        # touch cached document pages
        for page_id in page_ids:
            get_document_page(page_id)

        # filter uncached document pages
        uncached_document_page_ids = [
            page_id for page_id in page_ids if not has_document_page(page_id)
        ]

        # load uncached document pages
        def _load_document_page(page_id: str) -> DocumentPage:
            result = self.api.get(
                f"/end-user-gateway-service/artifacts/pages/{page_id}", timeout=5
            )

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
        self,
        document_ids: List[str],
        force_load: bool = False,
        load_pages: bool = False,
    ) -> List[Document]:
        """
        Load documents from the DeepSights API.

        Args:
            document_ids (List[str]): A list of document IDs to load.
            force_load (bool, optional): Whether to force load the documents, even if in cache. Defaults to False.
            load_pages (bool, optional): Whether to load the pages of the documents. Defaults to False.

        Returns:
            List[Document]: A list of loaded documents.
        """
        assert len(document_ids) < get_document_cache_size(), (
            "Cannot load more documents than the cache size."
        )

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
            result = self.api.get(
                f"/end-user-gateway-service/artifacts/{document_id}", timeout=5
            )

            # capitalize the first letter of the summary
            if result.get("summary") and len(result["summary"]) > 0:
                result["summary"] = result["summary"][0].upper() + result["summary"][1:]

            # map the document
            return Document.model_validate(result)

        newly_loaded_docs = run_in_parallel(_load_document, docs_to_load, max_workers=5)

        # Load pages if requested
        if load_pages:
            all_docs_needing_pages = newly_loaded_docs + [
                get_document(doc_id) for doc_id in docs_to_load_pages
            ]

            def _load_pages(document: Document):
                if not document.page_ids:
                    result = self.api.get(
                        f"/end-user-gateway-service/artifacts/{document.id}/page-ids",
                        timeout=5,
                    )
                    document.page_ids = result["ids"]
                return document.page_ids

            all_page_ids = run_in_parallel(
                _load_pages, all_docs_needing_pages, max_workers=5
            )

            # Flatten page ids
            flat_page_ids = [
                page_id for page_ids in all_page_ids for page_id in page_ids
            ]

            # Load actual pages
            self.document_pages_load(flat_page_ids)

        # Update cache with newly loaded documents and documents with newly loaded pages
        for doc in newly_loaded_docs:
            set_document(doc.id, doc)
        for doc_id in docs_to_load_pages:
            set_document(doc_id, get_document(doc_id))

        # Collect results
        return [get_document(doc_id) for doc_id in document_ids]
