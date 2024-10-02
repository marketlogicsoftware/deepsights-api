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
This module contains the user client for the DeepSights API, impersonating a given user.
"""

from deepsights.api.api import OAuthTokenAPI
from deepsights.userclient.resources import AnswerV2Resource, ReportResource


#################################################
class UserClient(OAuthTokenAPI):
    """
    This class defined the user client for DeepSights APIs, impersonating a given user.
    """

    answersV2: AnswerV2Resource
    reports: ReportResource

    #######################################
    def __init__(self, oauth_token: str) -> None:
        """
        Initializes the API client.

        Args:

            oauth_token (str): The OAuth token to be used for authentication.
        """
        super().__init__(
            endpoint_base="https://api.deepsights.ai/ds/v1",
            oauth_token=oauth_token,
        )

        self.answersV2 = AnswerV2Resource(self)
        self.reports = ReportResource(self)
