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
Shared test fixtures and configuration for the DeepSights API test suite.
"""

import json
import os
from pathlib import Path

try:
    # Load local environment variables from .env if available
    from dotenv import load_dotenv  # type: ignore

    # Load from project root by default
    dotenv_path = Path(".env")
    if dotenv_path.exists():
        load_dotenv(dotenv_path=dotenv_path, override=False)
except Exception:
    # If python-dotenv isn't installed or any error occurs, continue without failing
    pass

import pytest

import deepsights
from deepsights.userclient import UserClient


@pytest.fixture(scope="session")
def test_data():
    """
    Load shared test data from JSON file.

    Returns:
        dict: Test data containing embeddings, queries, and IDs for testing.
    """
    with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
        return json.load(f)


@pytest.fixture(scope="session")
def ds_client():
    """
    Create a shared DeepSights client instance for testing.

    Returns:
        deepsights.DeepSights: Configured client instance.
    """
    if not os.environ.get("DEEPSIGHTS_RUN_INTEGRATION") and not os.environ.get("DEEPSIGHTS_API_KEY"):
        pytest.skip("integration test requires DEEPSIGHTS_API_KEY or DEEPSIGHTS_RUN_INTEGRATION=1")
    return deepsights.DeepSights()


@pytest.fixture(scope="session")
def unauthorized_client():
    """
    Create a DeepSights client with invalid credentials for testing authentication.

    Returns:
        deepsights.DeepSights: Client with invalid API key.
    """
    if not os.environ.get("DEEPSIGHTS_RUN_INTEGRATION"):
        pytest.skip("integration test requires DEEPSIGHTS_RUN_INTEGRATION=1")
    return deepsights.DeepSights("invalid_api_key_2344234")


@pytest.fixture(scope="session")
def user_client():
    """
    Create a user client for testing user-specific functionality.

    Returns:
        UserClient: User client instance configured with valid email.
    """
    if not (os.environ.get("DEEPSIGHTS_RUN_INTEGRATION") or (os.environ.get("MIP_IDENTITY_VALID_EMAIL") and os.environ.get("MIP_API_KEY"))):
        pytest.skip("integration test requires MIP_IDENTITY_VALID_EMAIL and MIP_API_KEY or DEEPSIGHTS_RUN_INTEGRATION=1")
    from typing import cast

    valid_email = cast(str, os.environ.get("MIP_IDENTITY_VALID_EMAIL"))
    mip_api_key = cast(str, os.environ.get("MIP_API_KEY"))
    endpoint_base = "https://api.deepsights.ai/ds/v1"  # Default endpoint
    return UserClient.get_userclient(valid_email, mip_api_key, endpoint_base)


@pytest.fixture(scope="session")
def valid_email():
    """
    Get valid email for user client testing.

    Returns:
        str: Valid email address from environment.
    """
    if not (os.environ.get("DEEPSIGHTS_RUN_INTEGRATION") or os.environ.get("MIP_IDENTITY_VALID_EMAIL")):
        pytest.skip("integration test requires MIP_IDENTITY_VALID_EMAIL or DEEPSIGHTS_RUN_INTEGRATION=1")
    email = os.environ.get("MIP_IDENTITY_VALID_EMAIL")
    assert email is not None
    return email
