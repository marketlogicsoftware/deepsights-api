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
This module contains the tests for the MIP identity resolver.
"""

import os

from deepsights.deepsights._mip_identity import MIPIdentityResolver


def test_user_token_unknown_email():
    """
    Test case to verify that the OAuth token is None when the email is unknown.
    """
    mip_api_key = os.environ.get("MIP_API_KEY")
    mip_resolver = MIPIdentityResolver(mip_api_key)
    oauth_token = mip_resolver.get_oauth_token("foo@bar.de")

    assert oauth_token is None


def test_user_token_known_email(valid_email):
    """
    Test case to verify the retrieval of an OAuth token for a known email address.
    """
    mip_api_key = os.environ.get("MIP_API_KEY")
    mip_resolver = MIPIdentityResolver(mip_api_key)
    oauth_token = mip_resolver.get_oauth_token(valid_email)

    assert oauth_token is not None
