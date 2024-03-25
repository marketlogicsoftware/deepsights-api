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
This module contains the tests for the user client acccess.
"""

import os
import pytest
import deepsights

# set up the API client
ds = deepsights.DeepSights()

def get_valid_email():
    """
    Retrieves the valid email from the environment variable MIP_IDENTITY_VALID_EMAIL.

    Returns:
        str: The valid email address.
    """
    return os.environ["MIP_IDENTITY_VALID_EMAIL"]


def test_user_client_unknown_email():
    """
    Test case to verify that the user client raises an exception if the email is unknown.
    """
    with pytest.raises(ValueError):
        uc = ds.get_userclient("foo@bar.de")

def test_user_token_known_email():
    """
    Test case to verify the retrieval of a user client for a known email address.
    """
    uc = ds.get_userclient(get_valid_email())

    assert uc is not None
