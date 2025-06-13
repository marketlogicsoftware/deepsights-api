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
This module contains utility functions for ranking search results.
"""

import re
import shlex
from datetime import datetime, timezone
from typing import Any, Callable, List, Optional


#################################################
def rrf_merge_single(items: List, ranks: Callable, weights: List) -> List:
    """
    Merges the given items from a single list but with different ranks using Rank Reciprocal Fusion (RRF).

    Args:

        items (List): The items to be merged.
        ranks (function): The function to calculate the ranks of the items.
        weights (List): The weights to be used for the items.

    Returns:

        List: A list of merged, re-ranked items.
    """
    l = len(items)

    # calculate sum of ranks
    rank = {
        ix: sum([weight / (rank + l / 2) for weight, rank in zip(weights, ranks(item))])
        for ix, item in enumerate(items)
    }

    # sort by rank
    sorted_rank = sorted(rank.items(), key=lambda x: x[1], reverse=True)

    # merge items
    return [items[ix] for ix, _ in sorted_rank]


#################################################
def rrf_merge_multi(items: List[List], weights: List) -> List:
    """
    Merges the given items from multiple lists using Rank Reciprocal Fusion (RRF).
    Assumes the items in each list have an "id" attribute.

    Args:

        items (List[List]): The lists of items to be merged.
        weights (List): The weights to be used for each item list.

    Returns:

        List: A list of merged, re-ranked items.
    """
    rank_score = {}
    item_by_id = {}
    max_len = max([len(l) for l in items])

    # calculate sum of ranks
    for weight, item_list in zip(weights, items):
        for rank, item in enumerate(item_list):
            item_by_id[item.id] = item
            if item.id not in rank_score:
                rank_score[item.id] = 0

            rank_score[item.id] += weight / (rank + 1 + max_len / 2)

    # sort by rank
    sorted_rank = sorted(rank_score.items(), key=lambda x: x[1], reverse=True)

    # compile results
    return [item_by_id[item_id] for item_id, _ in sorted_rank]


#################################################
def promote_exact_matches(query: str, results: List[Any]) -> List[Any]:
    """
    Promotes exact and partial matches in the results based on the query.
    Assumes the items in the results have an "id" and "title" attribute.

    Args:

        query (str): The query.
        results (List[Any]): The list of results.

    Returns:

        List[Any]: The search results with exact and partial matches promoted.
    """
    if not query.strip() or not results:
        return results

    # determine terms in the query
    terms = shlex.split(query.lower())  # Convert to lowercase once
    if not terms:
        return results

    # compile regex patterns once for better performance
    exact_patterns = [
        re.compile(rf"(?:\b|\s|^){re.escape(term)}(?:\b|\s|$|\W)", re.IGNORECASE)
        for term in terms
    ]
    substring_patterns = [
        re.compile(rf"(?:\b|\s|^){re.escape(term)}", re.IGNORECASE) for term in terms
    ]

    exact_matches = set()
    substring_matches = set()

    # single pass through results to categorize matches
    for item in results:
        if not hasattr(item, "title") or not item.title:
            continue

        title = item.title
        item_id = item.id

        # check for exact matches
        if all(pattern.search(title) for pattern in exact_patterns):
            exact_matches.add(item_id)
        # check for substring matches (only if not already exact match)
        elif all(pattern.search(title) for pattern in substring_patterns):
            substring_matches.add(item_id)

    # re-rank results with optimized key function
    def sort_key(item):
        if item.id in exact_matches:
            return 0
        elif item.id in substring_matches:
            return 1
        else:
            return 2

    return sorted(results, key=sort_key)


#################################################
def rerank_by_recency(
    results: List[Any],
    recency_weight: Optional[float] = None,
) -> List[Any]:
    """
    Reranks the search results based on recency weight. If recency weight is None, the results are not reranked.
    Assumes the items in the results have a "publication_date" attribute.

    Args:

        results (List[Any]): The list of search results to be reranked.
        recency_weight (Optional[float]): The weight assigned to recency in the reranking process.

    Returns:

        List[Any]: The reranked search results.
    """
    if not results:
        return results

    # record score rank
    score_ranks = {result.id: rank for rank, result in enumerate(results)}

    # apply recency weight
    if recency_weight and 0 < recency_weight <= 1:
        current_time = datetime.now(timezone.utc)

        # calculate age in days, filtering out items without publication_date
        valid_items = []
        age_by_item_id = {}

        for r in results:
            if hasattr(r, "publication_date") and r.publication_date is not None:
                try:
                    age_days = (current_time - r.publication_date).days
                    # Handle negative ages (future dates) by setting to 0
                    age_by_item_id[r.id] = max(0, age_days)
                    valid_items.append(r)
                except (TypeError, AttributeError):
                    # Skip items with invalid publication_date
                    continue

        if not valid_items:
            # No valid publication dates found, skip reranking
            for rank, result in enumerate(results):
                if hasattr(result, "rank"):
                    result.rank = rank + 1
            return results

        # sort by age and create age ranks
        sorted_ages = sorted(age_by_item_id.items(), key=lambda x: x[1])
        age_ranks = {item_id: rank for rank, (item_id, _) in enumerate(sorted_ages)}

        # apply reciprocal rank fusion only to items with valid dates
        results = rrf_merge_single(
            results,
            ranks=lambda x: (
                score_ranks[x.id] + 1,
                age_ranks.get(x.id, len(results)) + 1,
            ),
            weights=(1 - recency_weight, recency_weight),
        )

    # record rank
    for rank, result in enumerate(results):
        if hasattr(result, "rank") or hasattr(result.__class__, "rank"):
            result.rank = rank + 1

    return results
