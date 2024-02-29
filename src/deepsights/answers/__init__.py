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
This module contains the functions to retrieve answers from the DeepSights API.
"""

from deepsights.answers.model import DocumentAnswer, DocumentAnswerPageReference
from deepsights.answers.answer import (
    answer_set_create,
    answer_set_wait_for_completion,
    answer_set_get,
    answer_set_get_sync,
)
from deepsights.answers.answer_v1 import answers_get
