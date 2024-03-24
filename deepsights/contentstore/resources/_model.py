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
This module contains the base models for the content store.
"""

from typing import Optional
from datetime import datetime
from pydantic import Field
from deepsights.utils import DeepSightsIdTitleModel


#################################################
class ContentStoreSearchResult(DeepSightsIdTitleModel):
    """
    Represents a search result from the content store.

    Attributes:

        description (str): The description of the item.
        image_url (str): The URL of the item's image.
        url (str): The URL of the item.
        publication_date (Optional[datetime], optional): The publication_date of the item's publication. Defaults to None.
        source (Optional[str], optional): The source of the item. Defaults to None.
        rank (Optional[int], optional): The final rank of the item in the search results. Defaults to None.
    """

    description: str = Field(description="The description of the item.")
    image_url: str = Field(description="The URL of the item's thumbnail image.")
    url: str = Field(description="The URL of the item.")
    publication_date: Optional[datetime] = Field(
        alias="published_at",
        default=None,
        description="The publication_date of the item's publication; may be None.",
    )
    source: Optional[str] = Field(
        alias="source_name",
        description="The name of the item's source; may be None.",
        default=None,
    )
    rank: Optional[int] = Field(
        default=None, description="The final rank of the item in the search results."
    )
