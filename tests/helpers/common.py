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
Common helper functions for tests.
"""

import re
import shlex


def equal_results(result, other):
    """
    Check if two search results are equivalent.

    Allows for same title due to duplicate content sources.

    Args:
        result: First result object to compare.
        other: Second result object to compare.

    Returns:
        bool: True if results are equivalent.
    """
    return result.id == other.id or result.title == other.title


def matches_query_terms(query, result):
    """
    Check if a result matches all terms in a query exactly.

    Args:
        query: Query string to match against.
        result: Result object with title attribute.

    Returns:
        bool: True if all query terms match in the result title.
    """
    return all(
        [
            re.search(
                rf"(?:\b|\s|^){re.escape(term)}(?:\b|\s|$|\W)",
                result.title,
                re.IGNORECASE,
            )
            for term in shlex.split(query)
        ]
    )
