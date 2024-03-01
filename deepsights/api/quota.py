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
This module contains the functions to retrieve quota information from the DeepSights API.
"""

from deepsights.api.api import DeepSights
from deepsights.api.model import APIProfile, QuotaStatus


#################################################
def api_get_profile(api: DeepSights) -> APIProfile:
    """
    Retrieves the API profile from the DeepSights API.

    Args:

        api (ds.DeepSights): The DeepSights API instance.

    Returns:

        APIProfile: The parsed API profile.
    """
    response = api.get("/static-resolver/api-key-attributes")
    return APIProfile.model_validate(response)


#################################################
def quota_get_status(api: DeepSights) -> QuotaStatus:
    """
    Get the quota status from the DeepSights API.

    Args:
    
        api (DeepSights): The DeepSights API object.

    Returns:

        QuotaStatus: The validated quota status response.
    """
    response = api.get("/static-resolver/quota")
    return QuotaStatus.model_validate(response)
