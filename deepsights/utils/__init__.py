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
This module contains utility functions and classes used by the DeepSights API.
"""

from deepsights.utils._cache import create_global_lru_cache
from deepsights.utils._ranking import (
    promote_exact_matches,
    rerank_by_recency,
    rrf_merge_multi,
    rrf_merge_single,
)
from deepsights.utils._utils import (
    PollingFailedError,
    PollingTimeoutError,
    poll_for_completion,
    run_in_parallel,
)
from deepsights.utils.model import (
    DeepSightsBaseModel,
    DeepSightsIdModel,
    DeepSightsIdTitleModel,
)

__all__ = [
    "run_in_parallel",
    "poll_for_completion",
    "PollingTimeoutError",
    "PollingFailedError",
    "create_global_lru_cache",
    "rrf_merge_multi",
    "rrf_merge_single",
    "rerank_by_recency",
    "promote_exact_matches",
    "DeepSightsBaseModel",
    "DeepSightsIdModel",
    "DeepSightsIdTitleModel",
]
