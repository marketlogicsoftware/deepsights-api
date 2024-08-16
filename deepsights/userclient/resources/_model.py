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
This module contains the model classes for answers.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import Field
from deepsights.utils import (
    DeepSightsBaseModel,
    DeepSightsIdModel,
    DeepSightsIdTitleModel,
)


#################################################
class Evidence(DeepSightsIdTitleModel):
    """
    Represents evidence.

    Attributes:

        synopsis (Optional[str]): The synopsis of the evidence; may be None.
        summary (Optional[str]): The summary of the evidence with respect to the current inquiry; may be None.
        text (Optional[str]): The text of the evidence; may be None.
        publication_date (Optional[datetime]): The publication date of the evidence.
        reference (Optional[str]): The quotation reference code of the evidence.
    """

    synopsis: Optional[str] = Field(
        alias="artifact_summary",
        description="The synopsis of the evidence; may be None.",
        default=None,
    )  

    summary: Optional[str] = Field(
        alias="summary",
        description="The summary of the evidence with respect to the current inquiry; may be None.",
        default=None,
    )

    text: Optional[str] = Field(
        alias="text",
        description="The text of the evidence; may be None.",
        default=None,
    )

    publication_date: Optional[datetime] = Field(
        description="The publication date of the evidence.", default=None
    )
    reference: Optional[str] = Field(
        alias="reference_id",
        description="The quotation reference code of the evidence.",
        default=None,
    )


#################################################
class DocumentPageEvidence(DeepSightsIdModel):
    """
    Represents a document page in evidence.

    Attributes:

        page_number (Optional[int], optional): The number of the page.
    """

    page_number: Optional[int] = Field(
        default=None, description="The number of the page (one-based)."
    )


#################################################
class DocumentEvidence(Evidence):
    """
    Represents evidence found in a document.

    Attributes:

        description (Optional[str]): The human-readable summary of the document.
        pages (List[DocumentPageSearchResult]): The list of pages in the document where the evidence is found.
    """

    pages: List[DocumentPageEvidence] = Field(
        alias="page_references",
        description="The list of pages in the document where the evidence is found.",
        default=[],
    )


#################################################
class ContentStoreSource(DeepSightsBaseModel):
    """
    Represents a content store item.

    Attributes:

        name (str): The name of the source.
        image_url (Optional[str]): The image url of the source, may be none∏∏
    """

    name: str = Field(
        alias="title",
        description="The name of the source",
    )
    image_url: Optional[str] = Field(
        description="The image url of the source, may be none.", default=None
    )


#################################################
class ContentStoreEvidence(Evidence):
    """
    Represents evidence for a content store item.

    Attributes:

        source (ContentStoreSource): The item's source.
        description (Optional[str]): The human-readable summary of the news item.
    """

    source: ContentStoreSource = Field(description="The item's source.")