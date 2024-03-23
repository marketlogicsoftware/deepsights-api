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
Sample code to use the DeepSights API.
"""

import json
import deepsights

# get the test embedding from JSON
# THIS REQUIRES THE TEST DATA TO BE AVAILABLE FROM GITHUB REPO
with open("tests/data/test_data.json", "rt", encoding="utf-8") as f:
    data = json.load(f)
    test_embedding = data["embedding"]
    test_question = data["question"]

#################################################
# DEEPSIGHTS API

# create a new instance of the DeepSights API, assuming api key is set in the environment as DEEPSIGHTS_API_KEY
ds = deepsights.DeepSights()

# get the API profile
profile = deepsights.api_get_profile(ds)

# get quota information
quota = deepsights.quota_get_status(ds)

# search document matches for an ADA-002 query vector
document_results = deepsights.documents_search(
    ds, query_embedding=test_embedding, max_results=10, min_score=0.0
)

# search again, but this time re-rank the results based on recency
document_results_recency = deepsights.documents_search(
    ds,
    query_embedding=test_embedding,
    max_results=10,
    recency_weight=0.7,
)

# load the docs with their pages; we might as well have passed "load_documents=True" to the search function
documents = deepsights.documents_load(
    ds,
    document_ids=[r.id for r in document_results],
    load_pages=True,
)

# get the first dod
top_document = documents[0]
print(top_document.title)

# what fields are available?
print(top_document.schema_human())

# obtain an answer set
answerset = deepsights.answerset_get_sync(
    ds,
    question=test_question,
)

#################################################
# CONTENTSTORE API

# create a new instance of the ContentStore API, assuming api key is set in the environment as CONTENTSTORE_API_KEY
cs = deepsights.ContentStore()

# search for news; no need for further loading, all content present in the search results
news_results = deepsights.news_search(
    cs,
    query=test_question,
    max_results=10,
)

# search for reports; no need for further loading, all content present in the search results
# news and reports also support explicit recency weighting
report_results = deepsights.secondary_search(
    cs,
    query=test_question,
    max_results=10,
    recency_weight=0.9,
)

# we can also use control hybrid search for news and reports; this will first combine recency weighting and then merge text & vector results
# note that document search currently does not expose the hybrid search functionality
hybrid_results = deepsights.secondary_search(
    cs,
    query=test_question,
    max_results=10,
    vector_weight=0.7,
    vector_fraction=0.5,
    recency_weight=0.9,
)

# and we can promote exact title matches to the top for hybrid or text search
# for pure full-text search, omit the query_embedding
hybrid_results_promote = deepsights.secondary_search(
    cs,
    query=test_question,
    max_results=10,
    promote_exact_match=True,
)
