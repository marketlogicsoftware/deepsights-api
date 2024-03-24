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
This module contains the base functions to interact with the DeepSights API.
"""

from deepsights.api.api import API
from deepsights.deepsights.resources import (
    QuotaResource,
    ReportResource,
    DocumentResource,
    AnswerResource,
)


#################################################
class DeepSights(API):
    """
    This class provides methods to interact with the DeepSights API.
    """

    quota: QuotaResource
    documents: DocumentResource
    answers: AnswerResource
    reports: ReportResource

    #######################################
    def __init__(self, api_key: str = None) -> None:
        """
        Initializes the API client.

        Args:

            api_key (str, optional): The API key to be used for authentication. If not provided, it will be fetched from the environment variable DEEPSIGHTS_API_KEY.
        """
        super().__init__(
            endpoint_base="https://api.deepsights.ai/ds/v1/",
            api_key=api_key,
            api_key_env_var="DEEPSIGHTS_API_KEY",
        )

        self.quota = QuotaResource(self)
        self.documents = DocumentResource(self)
        self.answers = AnswerResource(self)
        self.reports = ReportResource(self)
