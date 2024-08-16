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
from pydantic import Field
from deepsights.utils import DeepSightsIdModel
from deepsights.userclient.resources._model import (
    DocumentEvidence,
    ContentStoreEvidence,
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
        secondary_sources (List[ReportEvidence]): List of evidence from secondary sources used in the report.
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
    document_sources: List[DocumentEvidence] = Field(
        default=[], description="List of evidence from documents used in the report."
    )
    secondary_sources: List[ContentStoreEvidence] = Field(
        default=[],
        description="List of evidence from secondary sources used in the report.",
    )
    news_sources: List[ContentStoreEvidence] = Field(
        default=[], description="List of evidence from news sources used in the report."
    )
