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
import os

import deepsights
from deepsights.userclient import UserClient

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

print("=== User Client Examples ===")

# Method 1: Traditional approach - obtain a user client for a known email address
# This gets a token once and uses it (no auto-refresh)
uc = UserClient.get_userclient(
    "john.doe@acme.com", 
    os.environ.get('MIP_API_KEY'), 
    ds._endpoint_base
)
print(f"Traditional user client created for john.doe@acme.com")

# Method 2: Auto-refresh mode with configurable interval
# This automatically refreshes tokens every 10 minutes (600 seconds) by default
print("\n=== Auto-Refresh Token Management ===")

try:
    # Create user client with auto-refresh (default 10-minute intervals)
    auto_uc = UserClient(
        email="john.doe@acme.com",
        # api_key="your_mip_api_key_here"  # or set MIP_API_KEY environment variable
    )

    # Check token status
    token_info = auto_uc.get_token_info()
    print(f"Auto-refresh enabled: {token_info['auto_refresh_enabled']}")
    print(f"User email: {token_info['email']}")
    print(
        f"Refresh interval: {token_info['refresh_interval_seconds']} seconds ({token_info['refresh_interval_seconds'] / 60:.1f} minutes)"
    )
    print(f"Has valid token: {token_info['has_token']}")

    # Example with custom refresh interval (5 minutes for demo)
    frequent_refresh_uc = UserClient(
        email="john.doe@acme.com",
        # api_key="your_mip_api_key_here",
        auto_refresh_interval_seconds=300,  # Refresh every 5 minutes
    )

    print("\nCreated client with custom 5-minute refresh interval")

    # Manually trigger a token refresh if needed
    print("Demonstrating manual token refresh...")
    refresh_success = frequent_refresh_uc.manual_token_refresh()
    print(f"Manual refresh successful: {refresh_success}")

    # For long-running applications, you can stop auto-refresh when done
    print("Stopping auto-refresh for cleanup...")
    frequent_refresh_uc.stop_auto_refresh()

    # Use the auto-refresh client for API calls (tokens refresh automatically)
    uc = auto_uc  # Use auto-refresh client for remaining examples

except ValueError as e:
    print(f"Auto-refresh mode not available: {e}")
    print("Falling back to traditional mode...")
    # Fall back to traditional method if auto-refresh setup fails
    uc = UserClient.get_userclient(
        "john.doe@acme.com", 
        os.environ.get('MIP_API_KEY'), 
        ds._endpoint_base
    )

print("\n=== User Client Document Management ===")

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

print("\n=== AI-Generated Answers ===")

# obtain an answer set
answer = uc.answersV2.create_and_wait(
    question=test_question,
)
print(f"Answer: {answer.answer}")
print(f"Sources: {len(answer.document_sources)} documents cited")

print("\n=== Rate Limiting & Error Handling Demo ===")


# Demonstrate consistent rate limiting and error handling
def demonstrate_rate_limiting():
    """
    Demonstrates how the DeepSights API handles rate limiting consistently
    for both client-side and server-side scenarios.
    """
    print("🔄 Testing rate limiting behavior...")

    questions = [
        "What are the latest consumer trends in sustainability?",
        "How is Gen Z changing the retail landscape?",
        "What are emerging food consumption patterns?",
        "How do brand preferences differ across demographics?",
        "What drives customer loyalty in digital-first brands?",
    ]

    successful_requests = 0

    for i, question in enumerate(questions):
        try:
            print(f"\n📝 Processing question {i + 1}: {question[:50]}...")

            # This will hit client-side rate limits (10/minute for answers)
            answer_id = uc.answersV2.create(question)
            print(f"✅ Answer request created: {answer_id}")
            successful_requests += 1

        except deepsights.RateLimitError as e:
            print(f"🚫 Rate limit exceeded: {e}")

            if e.retry_after:
                print(f"⏱️  Client-side limit - suggested wait: {e.retry_after} seconds")
                print("   (In production, you'd implement your retry strategy here)")
            else:
                print("⏱️  Server-side limit - try again later")

            # In a real application, you might:
            # - Queue the request for later
            # - Wait and retry automatically
            # - Show user a progress indicator
            break

        except deepsights.AuthenticationError as e:
            print(f"🔐 Authentication failed: {e}")
            print("   Check your API keys and user permissions")
            break

        except deepsights.DeepSightsError as e:
            print(f"⚠️  API error: {e}")
            print("   This could be a temporary server issue")
            break

        except Exception as e:
            print(f"❌ Unexpected error: {type(e).__name__}: {e}")
            break

    print("\n📊 Rate limiting demo complete!")
    print(f"   Successfully processed: {successful_requests}/{len(questions)} requests")
    print("   Rate limit: 10 requests per 60 seconds for AI answers")

    # Best practice example
    print("\n💡 Best Practice Example:")
    print("   For production applications, implement exponential backoff:")
    print("   ```python")
    print("   try:")
    print("       response = uc.answersV2.create_and_wait(question)")
    print("   except deepsights.RateLimitError as e:")
    print("       wait_time = e.retry_after or 60  # Use provided time or fallback")
    print("       time.sleep(wait_time)")
    print("       # Retry logic here...")
    print("   ```")


# Run the demonstration
try:
    demonstrate_rate_limiting()
except Exception as e:
    print(f"Demo could not run: {e}")
    print("This is normal if running without proper API credentials")
