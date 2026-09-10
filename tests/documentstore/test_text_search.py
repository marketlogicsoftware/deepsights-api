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
Test the text_search function for the documentstore client.
"""

import pytest

from deepsights.exceptions import AuthenticationError
from tests.helpers.validation import assert_valid_text_search_result

pytestmark = pytest.mark.integration


def _text_search_or_skip(ds_client, **kwargs):
    """Run text_search, skipping when the API key's product does not expose the endpoint."""
    try:
        return ds_client.documentstore.documents.text_search(**kwargs)
    except AuthenticationError:
        pytest.skip("the API key's product does not grant access to text-searches")


def test_text_search_finds_document_by_title(ds_client):
    """
    Test that a lexical metadata search finds a known document by its own title.

    Lists one completed document from the corpus, then searches for its title and
    asserts the document is among the results.
    """
    _, documents = ds_client.documentstore.documents.list(page_size=1, status_filter=["COMPLETED"])
    if not documents or not documents[0].title:
        pytest.skip("no completed document with a title available in the test corpus")

    document = documents[0]
    results = _text_search_or_skip(ds_client, metadata_query=document.title, limit=25)

    assert len(results) > 0
    for result in results:
        assert_valid_text_search_result(result)
    assert document.id in [result.artifact.id for result in results]


def test_text_search_limit(ds_client, test_data):
    """
    Test that the limit parameter caps the number of results.
    """
    results = _text_search_or_skip(ds_client, content_query=test_data["question"], limit=3)

    assert isinstance(results, list)
    assert len(results) <= 3
    for result in results:
        assert_valid_text_search_result(result)
