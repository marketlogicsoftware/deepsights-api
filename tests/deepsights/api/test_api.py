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
This module contains the tests for the DeepSights API.
"""

import pytest
import requests
import deepsights


def test_ds_api_authentication():
    """
    Test case for DeepSights API authentication.

    This test verifies that an HTTPError with status code 401 is raised when attempting to
    get the profile using an invalid API key.

    """
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        deepsights.api_get_profile(deepsights.DeepSights(api_key="1234567890"))

    assert exc.value.response.status_code == 401


def test_cs_api_authentication():
    """
    Test case for ContentStore API authentication.

    This test verifies that an HTTPError with status code 401 is raised when attempting to get the profile
    using an invalid API key.

    """
    with pytest.raises(requests.exceptions.HTTPError) as exc:
        deepsights.api_get_profile(deepsights.ContentStore(api_key="1234567890"))

    assert exc.value.response.status_code == 401


def test_ds_api_attributes():
    """
    Test case to verify the attributes of the DeepSights API response.
    """
    r = deepsights.api_get_profile(deepsights.DeepSights())

    assert r.app is not None
    assert r.tenant is not None


def test_ds_quota_info():
    """
    Test case for checking the quota information of DeepSights API.

    This test verifies that the quota information returned by the API is valid.
    It checks the day quota and minute quota, ensuring that they are not None,
    and that the quota reset time and quota usage are valid.
    """
    r = deepsights.quota_get_status(deepsights.DeepSights())

    assert r.day_quota is not None
    assert r.day_quota.quota_reset_at is not None
    assert r.day_quota.quota_used >= 0

    assert r.minute_quota is not None
    assert r.minute_quota.quota_reset_at is not None
    assert r.minute_quota.quota_used >= 0
