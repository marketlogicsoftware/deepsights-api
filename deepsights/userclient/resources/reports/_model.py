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
This module contains the model classes for reports.
"""

from typing import Optional, List
from datetime import datetime
from pydantic import Field
from deepsights.utils import DeepSightsIdModel, DeepSightsIdTitleModel


#################################################
class ReportEvidence(DeepSightsIdTitleModel):
    """
    Represents evidence related to a report.

    Attributes:

        summary (Optional[str]): The summary of the evidence with respect to the report's question.
        publication_date (Optional[datetime]): The publication date of the evidence.
        reference (Optional[str]): The quotation reference code of the evidence.
    """

    evidence_summary: Optional[str] = Field(
        alias="summary",
        description="The summary of the evidence with respect to the report's question.",
    )
    publication_date: Optional[datetime] = Field(
        description="The publication date of the evidence.",
        default=None
    )
    reference: Optional[str] = Field(
        alias="reference_id",
        description="The quotation reference code of the evidence.",
    )


#################################################
class DocumentPageReportEvidence(DeepSightsIdModel):
    """
    Represents a document page in a report evidence.

    Attributes:

        page_number (Optional[int], optional): The number of the page.
    """

    page_number: Optional[int] = Field(
        default=None, description="The number of the page (one-based)."
    )


#################################################
class DocumentReportEvidence(ReportEvidence):
    """
    Represents evidence found in a document for a report.

    Attributes:

        description (Optional[str]): The human-readable summary of the document.
        pages (List[DocumentPageSearchResult]): The list of pages in the document where the evidence is found.
    """

    description: Optional[str] = Field(
        alias="artifact_summary",
        description="The human-readable summary of the document.",
    )
    pages: List[DocumentPageReportEvidence] = Field(
        alias="page_references",
        description="The list of pages in the document where the evidence is found.",
        default=[],
    )


#################################################
class NewsReportEvidence(ReportEvidence):
    """
    Represents evidence for a news report.

    Attributes:

        source (Optional[str]): The name of the item's source; may be None.
        description (Optional[str]): The human-readable summary of the news item.
    """

    source: Optional[str] = Field(
        description="The name of the item's source; may be None.", default=None
    )
    description: Optional[str] = Field(
        alias="summary",
        description="The human-readable summary of the news item.",
    )


#################################################
class Report(DeepSightsIdModel):
    """
    Represents a report generated by the DeepSights API.

    Attributes:

        status (str): The processing status of the report.
        permission_validation (str): The permission validation of the report for the caller.
        question (str): The question that the report is answering.
        topic (str, optional): The AI-generated topic of the report.
        summary (str, optional): The summary text of the report in markdown format.
        document_sources (List[ReportEvidence]): List of evidence from documents used in the report.
        news_sources (List[ReportEvidence]): List of evidence from news sources used in the report.
    """

    permission_validation: str = Field(
        description="The permission validation of the report for the caller.",
    )
    status: str = Field(description="The processing status of the report.")
    question: str = Field(description="The question that the report is answering.")
    topic: Optional[str] = Field(
        default=None, description="The AI-generated topic of the report."
    )
    summary: Optional[str] = Field(
        default=None, description="The summary text of the report in markdown format."
    )
    document_sources: List[DocumentReportEvidence] = Field(
        default=[], description="List of evidence from documents used in the report."
    )
    news_sources: List[NewsReportEvidence] = Field(
        default=[], description="List of evidence from news sources used in the report."
    )
