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
This module contains the tests for the DeepSights API.
"""

import pytest

from deepsights.exceptions import AuthenticationError
from tests.helpers.validation import (
    assert_valid_quota_profile,
    assert_valid_quota_status,
)


def test_ds_api_authentication(unauthorized_client):
    """
    Test case for DeepSights API authentication.

    This test verifies that an AuthenticationError is raised when attempting to
    get the profile using an invalid API key.

    """
    with pytest.raises(AuthenticationError) as exc:
        unauthorized_client.quota.get_profile()

    assert "Invalid API key or insufficient permissions" in str(exc.value)


def test_ds_quota_info(ds_client):
    """
    Test case for checking the quota information of DeepSights API.

    This test verifies that the quota information returned by the API is valid.
    It checks the day quota and minute quota, ensuring that they are not None,
    and that the quota reset time and quota usage are valid.
    """
    status = ds_client.quota.get_status()

    assert_valid_quota_status(status)


def test_ds_api_profile(ds_client):
    """
    Test case to verify the profile of the DeepSights API response.
    """
    profile = ds_client.quota.get_profile()

    assert_valid_quota_profile(profile)
