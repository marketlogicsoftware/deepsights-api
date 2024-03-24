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
This module contains the resource to retrieve quota information from the DeepSights API.
"""

from deepsights.api import APIResource
from deepsights.deepsights.resources.quota._model import APIProfile, QuotaStatus


#################################################
class QuotaResource(APIResource):
    """
    Represents a resource for retrieving quota information from the DeepSights API.
    """

    #################################################
    def get_profile(self) -> APIProfile:
        """
        Retrieves the API profile from the DeepSights API.

        Args:

            api (ds.DeepSights): The DeepSights API instance.

        Returns:

            APIProfile: The parsed API profile.
        """
        response = self.api.get("/static-resolver/api-key-attributes")
        return APIProfile.model_validate(response)

    #################################################
    def get_status(self) -> QuotaStatus:
        """
        Get the quota status from the DeepSights API.

        Args:

            api (API): The DeepSights API object.

        Returns:

            QuotaStatus: The validated quota status response.
        """
        response = self.api.get("/static-resolver/quota")
        return QuotaStatus.model_validate(response)
