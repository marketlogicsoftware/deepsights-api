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
This module contains the resource to interact with documents via the DeepSights API.
"""

from deepsights.api import APIResource

from deepsights.documentstore.resources.documents._upload import (
    document_upload,
    document_wait_for_upload,
)
from deepsights.documentstore.resources.documents._download import document_download
from deepsights.documentstore.resources.documents._delete import (
    documents_delete,
    document_wait_for_deletion,
)
from deepsights.documentstore.resources.documents._load import (
    documents_load,
    document_pages_load,
)
from deepsights.documentstore.resources.documents._search import (
    documents_search,
    document_pages_search,
)
from deepsights.documentstore.resources.documents._list import (
    documents_list,
)



#################################################
class DocumentResource(APIResource):
    """
    Represents a resource to interact with documents via the DeepSights API.
    """

    upload = document_upload
    wait_for_upload = document_wait_for_upload
    delete = documents_delete
    wait_for_delete = document_wait_for_deletion
    load = documents_load
    load_pages = document_pages_load
    download = document_download
    search = documents_search
    search_pages = document_pages_search
    list = documents_list
