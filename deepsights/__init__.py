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
This module contains the client library to interact with the Market Logic DeepSights and ContentStore APIs.
"""

from deepsights import exceptions
from deepsights.deepsights import DeepSights
from deepsights.userclient import UserClient
from deepsights.documentstore.resources import SortingField, SortingOrder
from deepsights.exceptions import AuthenticationError, DeepSightsError, RateLimitError

__all__ = [
    "SortingField",
    "SortingOrder",
    "DeepSights",
    "exceptions",
    "UserClient",
    "AuthenticationError",
    "DeepSightsError",
    "RateLimitError",
]
