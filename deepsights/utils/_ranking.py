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
This module contains utility functions for ranking search results.
"""

import re
import shlex
from datetime import datetime, timezone
from typing import List, Callable


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
def promote_exact_matches(query: str, results: List) -> List:
    """
    Promotes exact and partial matches in the results based on the query.
    Assumes the items in the results have an "id" and "title" attribute.

    Args:

        query (str): The query.
        results (List[BaseModel]): The list of results.

    Returns:

        List: The search results with exact and partial matches promoted.
    """
    # determine terms in the query
    terms = shlex.split(query)

    # find documents with exact title matches, using regex
    exact_matches = [
        item.id
        for item in results
        if all(
            re.search(
                rf"(?:\b|\s|^){re.escape(term)}(?:\b|\s|$|\W)",
                item.title,
                re.IGNORECASE,
            )
            is not None
            for term in terms
        )
    ]

    # find documents with starting substring title matches, using regex
    substring_matches = [
        item.id
        for item in results
        if not item.id in exact_matches
        and all(
            re.search(
                rf"(?:\b|\s|^){re.escape(term)}",
                item.title,
                re.IGNORECASE,
            )
            is not None
            for term in terms
        )
    ]

    # now re-rank to put docs with exact matches first, then with partial matches, then the rest in original order
    results = sorted(
        results,
        key=lambda x: (
            0 if x.id in exact_matches else 1 if x.id in substring_matches else 2
        ),
    )

    return results


#################################################
def rerank_by_recency(
    results: List,
    recency_weight: float = None,
) -> List:
    """
    Reranks the search results based on recency weight. If recency weight is None, the results are not reranked.
    Assumes the items in the results have a "publication_date" attribute. 

    Args:

        results (List): The list of search results to be reranked.
        recency_weight (float, optional): The weight assigned to recency in the reranking process.

    Returns:
    
        List: The reranked search results.
    """
    # record score rank
    score_ranks = {}
    for rank, result in enumerate(results):
        score_ranks[result.id] = rank

    # apply recency weight
    if recency_weight:
        # calculate age in days
        age_by_item_id = {}
        for r in results:
            age_by_item_id[r.id] = (
                (datetime.now(timezone.utc) - r.publication_date).days if r.publication_date else None
            )

        age_by_item_id = {
            k: v for k, v in sorted(age_by_item_id.items(), key=lambda item: item[1])
        }

        # record age rank
        age_ranks = {k: i for i, k in enumerate(age_by_item_id)}

        # apply reciprocal rank fusion
        results = rrf_merge_single(
            results,
            ranks=lambda x: (score_ranks[x.id]+1, age_ranks[x.id]+1),
            weights=(1 - recency_weight, recency_weight),
        )

    # record rank
    for rank, result in enumerate(results):
        result.rank = rank + 1

    return results
