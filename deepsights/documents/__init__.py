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
This module contains the functions to retrieve documents from the DeepSights API.
"""

from deepsights.documents._cache import (
    set_document,
    has_document,
    get_document,
    remove_document,
    get_document_cache_size,
    set_document_page,
    has_document_page,
    get_document_page,
    remove_document_page,
    get_document_page_cache_size,
)
from deepsights.documents.model import (
    Document,
    DocumentPage,
    DocumentPageSearchResult,
    DocumentSearchResult,
)
from deepsights.documents.upload import document_upload, document_wait_for_processing
from deepsights.documents.download import document_download
from deepsights.documents.delete import documents_delete, document_wait_for_deletion
from deepsights.documents.load import (
    documents_load,
    document_pages_load,
)
from deepsights.documents.search import documents_search, document_pages_search
