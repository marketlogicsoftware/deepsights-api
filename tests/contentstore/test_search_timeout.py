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
Unit tests for the timeout and retry behavior of content store searches.
"""

from typing import Any, List

import pytest
from requests.exceptions import ConnectionError as RequestsConnectionError
from requests.exceptions import Timeout
from tenacity import wait_none

from deepsights.api.api import API, MAX_ATTEMPTS
from deepsights.contentstore.contentstore import ContentStore
from deepsights.contentstore.resources._search import SEARCH_TIMEOUT


class _DummyResponse:
    def __init__(self, status_code: int = 200) -> None:
        self.status_code = status_code

    def json(self) -> Any:
        return {"items": []}


@pytest.fixture(name="client")
def _client() -> ContentStore:
    return ContentStore(api_key="test-key")


@pytest.fixture(name="no_retry_wait")
def _no_retry_wait(monkeypatch) -> None:
    """Drop the exponential backoff so retrying tests don't actually sleep."""
    monkeypatch.setattr(API.post.retry, "wait", wait_none())


def _capture_post(client: ContentStore, calls: List[Any], raises: Exception | None = None):
    def fake_post(url: str, params: Any = None, json: Any = None, timeout: Any = None, headers: Any = None):
        calls.append({"url": url, "timeout": timeout})
        if raises is not None:
            raise raises
        return _DummyResponse()

    client._session.post = fake_post  # type: ignore[method-assign]


# every search entry point of both content store resources; they share one backend
_SEARCHES = {
    "secondary-hybrid": lambda c: c.secondary.search(query="test"),
    "secondary-text": lambda c: c.secondary.text_search(query="test"),
    "secondary-vector": lambda c: c.secondary.vector_search(query_embedding=[0.1] * 1536),
    "news-hybrid": lambda c: c.news.search(query="test"),
    "news-text": lambda c: c.news.text_search(query="test"),
    "news-vector": lambda c: c.news.vector_search(query_embedding=[0.1] * 1536),
}


@pytest.mark.parametrize("search", _SEARCHES.values(), ids=_SEARCHES.keys())
def test_searches_use_the_longer_timeout(client, search):
    calls: List[Any] = []
    _capture_post(client, calls)

    search(client)

    assert len(calls) == 1
    assert calls[0]["timeout"] == SEARCH_TIMEOUT == 30


@pytest.mark.parametrize("search", _SEARCHES.values(), ids=_SEARCHES.keys())
def test_searches_do_not_retry_on_timeout(client, no_retry_wait, search):
    calls: List[Any] = []
    _capture_post(client, calls, raises=Timeout("too slow"))

    with pytest.raises(Timeout):
        search(client)

    assert len(calls) == 1


@pytest.mark.parametrize("search", _SEARCHES.values(), ids=_SEARCHES.keys())
def test_searches_retry_on_connection_error(client, no_retry_wait, search):
    calls: List[Any] = []
    _capture_post(client, calls, raises=RequestsConnectionError("connection reset"))

    with pytest.raises(RequestsConnectionError):
        search(client)

    assert len(calls) == MAX_ATTEMPTS == 2


def test_non_search_requests_keep_the_default_timeout_and_retry_timeouts(client, no_retry_wait):
    calls: List[Any] = []
    _capture_post(client, calls, raises=Timeout("too slow"))

    with pytest.raises(Timeout):
        client.post("item-service/items/_something-else", body={})

    assert len(calls) == MAX_ATTEMPTS
    assert calls[0]["timeout"] == client._default_timeout


def test_searches_keep_the_policy_in_unified_token_mode(no_retry_wait):
    # the unified token mixin overrides post(), so it has to forward the opt-out too
    client = ContentStore.with_unified_token(unified_token="token", refresh_callback=lambda _token: "new-token")
    calls: List[Any] = []
    _capture_post(client, calls, raises=Timeout("too slow"))

    with pytest.raises(Timeout):
        client.secondary.search(query="test")

    assert len(calls) == 1
    assert calls[0]["timeout"] == SEARCH_TIMEOUT
