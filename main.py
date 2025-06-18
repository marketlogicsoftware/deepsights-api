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
#
# create a new instance of the DeepSights API, assuming api key is set in the environment as DEEPSIGHTS_API_KEY
ds = deepsights.DeepSights()

# get the API profile
profile = ds.quota.get_profile()

# get quota information
quota = ds.quota.get_status()

# hybrid search combining text and vector search
hybrid_results = ds.documentstore.documents.search(
    query="consumer behavior trends 2024", extended_search=False
)

print("=== Document Store Hybrid Search Results ===")
for result in hybrid_results:
    print(f"📄 {result.artifact_title}")
    print(
        f"📝 {result.artifact_summary[:100]}..."
        if result.artifact_summary
        else "No summary"
    )
    print(f"📑 {len(result.page_references)} relevant pages\n")

# search document matches for an ADA-002 query vector (legacy approach)
document_results = ds.documentstore.documents.search_documents(
    query_embedding=test_embedding, max_results=10, min_score=0.0
)

# load the docs with their pages
documents = ds.documentstore.documents.load(
    document_ids=[r.id for r in document_results],
    load_pages=True,
)

# get the first doc
if documents:
    top_document = documents[0]
    print(f"Top document: {top_document.title}")

    # what fields are available?
    print(top_document.schema_human())

#################################################
# CONTENTSTORE API
#
# for this to work, we assume the api key was set in the environment as CONTENTSTORE_API_KEY

# search for news; no need for further loading, all content present in the search results
news_results = ds.contentstore.news.search(
    query=test_question,
    max_results=10,
)

# search for reports; no need for further loading, all content present in the search results
# news and reports also support explicit recency weighting
secondary_results = ds.contentstore.secondary.search(
    query=test_question,
    max_results=10,
    recency_weight=0.9,
)

# we can also use control hybrid search for news and reports; this will first combine recency weighting and then merge text & vector results
# note that document store now supports hybrid search via documents.search()
cs_hybrid_results = ds.contentstore.secondary.search(
    query=test_question,
    max_results=10,
    vector_weight=0.7,
    vector_fraction=0.5,
    recency_weight=0.9,
)


#################################################
# USERCLIENT API
#
# for this to work, we assume the api key for user resolution was set in the environment as MIP_API_KEY

# obtain a user client for a known email address
uc = ds.get_userclient("john.doe@acme.com")

print("=== User Client Document Management ===")

# list documents with user-specific access
total_docs, user_documents = uc.documents.documents_list(
    page_size=10, sort_field="creation_date", sort_order="DESC"
)
print(f"Found {total_docs} documents accessible to user")

# hybrid search through user client
user_hybrid_results = uc.documents.search(
    query="consumer behavior insights", extended_search=False
)
print(f"User hybrid search returned {len(user_hybrid_results)} results")

# topic search with AI analysis (user client only)
topic_results = uc.search.topic_search(
    query="sustainable packaging trends", extended_search=False
)
print(f"Topic search returned {len(topic_results)} results")
for result in topic_results[:2]:  # Show first 2
    print(f"📄 {result.artifact_title}")
    print(f"📊 Relevance: {result.relevance_class}")
    print(
        f"📝 Summary: {result.artifact_summary[:100]}..."
        if result.artifact_summary
        else "No summary"
    )
    print(f"📑 {len(result.page_references)} relevant pages\n")

# load specific documents with pages (if any found)
if user_documents:
    doc_ids = [doc.id for doc in user_documents[:2]]  # First 2 documents
    loaded_docs = uc.documents.documents_load(document_ids=doc_ids, load_pages=True)
    print(f"Loaded {len(loaded_docs)} documents with pages")

    # load specific document pages
    if loaded_docs and loaded_docs[0].page_ids:
        page_ids = loaded_docs[0].page_ids[:3]  # First 3 pages
        pages = uc.documents.document_pages_load(page_ids)
        print(f"Loaded {len(pages)} individual pages")

print("=== AI-Generated Answers ===")

# obtain an answer set
answer = uc.answersV2.create_and_wait(
    question=test_question,
)
print(f"Answer: {answer.answer}")
print(f"Sources: {len(answer.document_sources)} documents cited")
