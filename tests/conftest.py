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
    return deepsights.DeepSights()


@pytest.fixture(scope="session")
def unauthorized_client():
    """
    Create a DeepSights client with invalid credentials for testing authentication.

    Returns:
        deepsights.DeepSights: Client with invalid API key.
    """
    return deepsights.DeepSights("invalid_api_key_2344234")


@pytest.fixture(scope="session")
def user_client():
    """
    Create a user client for testing user-specific functionality.

    Returns:
        UserClient: User client instance configured with valid email.
    """
    valid_email = os.environ["MIP_IDENTITY_VALID_EMAIL"]
    mip_api_key = os.environ.get("MIP_API_KEY")
    endpoint_base = "https://api.deepsights.ai/ds/v1"  # Default endpoint
    return UserClient.get_userclient(valid_email, mip_api_key, endpoint_base)


@pytest.fixture(scope="session")
def valid_email():
    """
    Get valid email for user client testing.

    Returns:
        str: Valid email address from environment.
    """
    return os.environ["MIP_IDENTITY_VALID_EMAIL"]
