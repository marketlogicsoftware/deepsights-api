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
This module contains the functions to list documents from the DeepSights API.
"""

from typing import List
from deepsights.api import APIResource
from deepsights.documentstore.resources.documents._model import Document
from deepsights.documentstore.resources.documents._cache import set_document


#################################################
class SortingOrder:
    """
    Represents the sorting order for documents.
    """

    ASCENDING = "ASC"
    DESCENDING = "DESC"


#################################################
class SortingField:
    """
    Represents the sorting field for documents.
    """

    TITLE = "title"
    PUBLICATION_DATE = "publication_date"
    CREATION_DATE = "origin.creation_time"


#################################################
def documents_list(
    resource: APIResource,
    page_size: int = 50,
    page_number: int = 0,
    sort_order: str = SortingOrder.DESCENDING,
    sort_field: str = SortingField.CREATION_DATE,
    status_filter: List[str] = [],
):
    """
    List documents from the DeepSights API.

    Args:

        resource (APIResource): An instance of the DeepSights API resource.
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
    ], "The sort field must be 'title', 'publication_date', or 'origin.creation_time'."

    # construct
    body = {
        "size": page_size,
        "page": page_number,
        "sorting": {"field_name": sort_field, "sorting_direction": sort_order}
    }
    if status_filter:
        body["statuses"] = status_filter

    # fetch ids
    result = resource.api.post(
        "/artifact-service/artifacts/_search",
        body=body,
    )

    # get results
    total_results = result["total_items"]
    documents = [Document.model_validate(result) for result in result["items"]]

    # set documents
    for document in documents:
        set_document(document.id, document)

    return total_results, documents
