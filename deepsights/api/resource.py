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
This module contains the base class for all resources in an API. 
"""


from deepsights.api.api import API


#################################################
class APIResource:
    """
    Represents a resource in the API.

    Args:
        api (API): The API instance associated with the resource.
    """

    def __init__(self, api: API) -> None:
        """
        Initializes a new instance of the APIResource class.

        Args:
            api (API): The API instance associated with the resource.
        """
        self.api = api
