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
This module contains the tests for the user client access.
"""

import os

import pytest

from deepsights.userclient import UserClient


def test_user_client_unknown_email(ds_client):
    """
    Test case to verify that the user client raises an exception if the email is unknown.
    """
    mip_api_key = os.environ.get("MIP_API_KEY")
    endpoint_base = ds_client._endpoint_base
    with pytest.raises(ValueError):
        uc = UserClient.get_userclient("foo@bar.de", mip_api_key, endpoint_base)


def test_user_token_known_email(ds_client, valid_email):
    """
    Test case to verify the retrieval of a user client for a known email address.
    """
    mip_api_key = os.environ.get("MIP_API_KEY")
    endpoint_base = ds_client._endpoint_base
    uc = UserClient.get_userclient(valid_email, mip_api_key, endpoint_base)

    assert uc is not None
