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
Test the documents_list function
"""

import deepsights


def test_document_list(ds_client):
    number_of_results, documents = ds_client.documentstore.documents.list(
        page_size=10,
        page_number=0,
        sort_order=deepsights.SortingOrder.DESCENDING,
        sort_field=deepsights.SortingField.CREATION_DATE,
        status_filter=["COMPLETED"],
    )

    assert number_of_results >= 10
    assert len(documents) == 10

    for document in documents:
        assert document.id is not None
        assert document.title is not None or document.ai_generated_title is not None
        assert document.status is not None
