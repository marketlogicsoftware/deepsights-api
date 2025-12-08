# 🤖💡 deepsights-api

[![PyPI](https://img.shields.io/pypi/v/deepsights-api.svg)](https://pypi.org/project/deepsights-api/) [![Changelog](https://img.shields.io/github/v/release/marketlogicsoftware/deepsights-api?include_prereleases&label=changelog)](https://github.com/marketlogicsoftware/deepsights-api/releases) [![Tests](https://img.shields.io/github/actions/workflow/status/marketlogicsoftware/deepsights-api/run_tests.yml)](https://github.com/marketlogicsoftware/deepsights-api/actions/workflows/run_tests.yml) [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/marketlogicsoftware/deepsights-api/blob/main/LICENSE)

The official Python client library for the [DeepSights API](https://apiportal.mlsdevcloud.com/deep-sights) - the first AI assistant trained specifically for trusted market insights.

## Why DeepSights API?

Transform your market research into actionable business intelligence with AI that delivers **60% higher quality responses** than generic alternatives. DeepSights enables data scientists, analysts, and insight teams to:

- **Boost productivity by 70%** with AI-powered market insights
- **Save 7+ hours per research session** through intelligent automation
- **Integrate market intelligence** directly into business systems via AI-to-AI workflows
- **Trust your results** - only cites verified, trusted sources from your knowledge base

Perfect for B2C brands, enterprises, and research teams who need reliable market insights at scale.

**Requirements:** Python 3.10 - 3.12 | **Support:** [GitHub Issues](https://github.com/marketlogicsoftware/deepsights-api/issues)

## Scope

`deepsights-api` bundles access to various subsystems.

### Document Store

The **Document Store** hosts all customer-owned documents, such as presentations and reports. The `documentstore` API exposes lifecycle management, search and access to documents, as well as custom taxonomy management for organizing and classifying content.

### Custom Taxonomies

The **Custom Taxonomies** feature allows you to create and manage hierarchical classification systems for your documents. Taxonomies consist of:
- **Taxonomy**: A named classification system (e.g., "Product Categories", "Regions")
- **Taxon Types**: Classification levels within a taxonomy (e.g., "Country", "City")
- **Taxons**: Individual classification values with optional parent-child relationships (e.g., "Germany" → "Berlin")

### Content Store

The **Content Store** holds public and paid 3rd party content, including industry news and secondary sources. The `contentstore` API exposes search and access to this content.

### User Client

The **User Client** serves to impersonate existing platform users with their access permissions. The `userclient` API supports obtaining AI-generated answers and reports in response to business questions, as well as document management operations with user-specific permissions including document listing, loading, page access, hybrid search, and topic search capabilities.


## Search Methods

| Area | Method | Type | Notes | Returns |
|--|--|--|--|--|
| Document Store | `ds.documentstore.documents.search(query, extended_search=False, taxonomy_filters=None)` | Hybrid | Text + semantic; query ≤512 chars; optional taxonomy filtering | `List[HybridSearchResult]` |
| Document Store | `ds.documentstore.documents.topic_search(query, extended_search=False, taxonomy_filters=None)` | Topic | AI topic analysis; query ≤512 chars; optional taxonomy filtering | `List[TopicSearchResult]` |
| Document Store | `ds.documentstore.documents.search_pages(query_embedding, min_score=0.7, max_results=50, load_pages=False)` | Vector (pages, deprecated) | Deprecated; use hybrid search instead | `List[DocumentPageSearchResult]` |
| Document Store | `ds.documentstore.documents.search_documents(...)` | Vector (docs) | Deprecated; use hybrid search instead | `List[DocumentSearchResult]` |
| Content Store (News) | `ds.contentstore.news.search(query, ..., vector_fraction, vector_weight, recency_weight)` | Hybrid | Languages/date filters, optional evidence filter; max_results ≤250 | `List[NewsSearchResult]` |
| Content Store (News) | `ds.contentstore.news.vector_search(query_embedding, ..., recency_weight)` | Vector | Embedding length 1536; max_results ≤100 | `List[NewsSearchResult]` |
| Content Store (News) | `ds.contentstore.news.text_search(query, ..., sort_descending, offset)` | Text | `query=None` sorts by date; supports languages/date filters | `List[NewsSearchResult]` |
| Content Store (Secondary) | `ds.contentstore.secondary.search(query, ..., vector_fraction, vector_weight, recency_weight)` | Hybrid | Same as News; item type REPORTS | `List[SecondarySearchResult]` |
| Content Store (Secondary) | `ds.contentstore.secondary.vector_search(query_embedding, ..., recency_weight)` | Vector | Embedding length 1536; max_results ≤100 | `List[SecondarySearchResult]` |
| Content Store (Secondary) | `ds.contentstore.secondary.text_search(query, ..., sort_descending, offset)` | Text | `query=None` sorts by date; supports languages/date filters | `List[SecondarySearchResult]` |
| User Client | `user_client.documents.search(query, extended_search=False)` | Hybrid (user-context) | Permissions-aware; query ≤512 chars | `List[HybridSearchResult]` |
| User Client | `user_client.documents.topic_search(query, extended_search=False)` | Topic | AI topic analysis; query ≤512 chars | `List[TopicSearchResult]` |

Notes
- All document/content vector searches require 1536-dimensional embeddings.
- Content Store search methods support language and date-range filters; vector searches accept optional `recency_weight`.
- `search_documents(...)` and `search_documents_pages(...)` are deprecated in favor of hybrid search.

## Getting started

### Installation

Install this library using `pip`; we recommend installing it in a [virtualenv](https://virtualenv.pypa.io/en/latest/).

```shell
pip install deepsights-api
```

### API keys

[Contact us](https://apiportal.mlsdevcloud.com/get-started#Get_API_key) to obtain your API key(s) (may require commercial add-on).

| API Key | Scope |
|--|--|
| DEEPSIGHTS | Required to use `deepsights-api` and the `documentstore` functions |
| CONTENTSTORE | Optional key to access the `contentstore` functions |
| MIP | Optional key to access the `userclient` functions for customers utilizing the core Market Logic platform |

**Note that your API key may be authorized to access only a subset of the API endpoints.**

Configure your api keys either in your environment, or provide it as an argument to the API constructor.

```shell
DEEPSIGHTS_API_KEY = <your DeepSights API key>
CONTENTSTORE_API_KEY = <your ContentStore API key; optional>
MIP_API_KEY = <your MIP API key; optional>
```

then

```Python
import deepsights

# with keys from environment
ds = deepsights.DeepSights()

# OR with explicit key
ds = deepsights.DeepSights(
    ds_api_key="<your DEEPSIGHTS API key>",
    cs_api_key="<your CONTENTSTORE API key>",
    mip_api_key="<your MIP API key>"
)
```


### Quick Start Examples

#### AI-Powered Business Questions
```python
import os
import deepsights
from deepsights.userclient import UserClient

# Initialize with API keys from environment
ds = deepsights.DeepSights()

# Get user client for AI-generated insights
uc = UserClient.get_userclient(
    "analyst@company.com",
    os.environ.get('MIP_API_KEY'),
    "https://api.deepsights.ai/ds/v1"
)

# Ask business questions and get AI answers
response = uc.answersV2.create_and_wait(
    "What are emerging food consumption moments for Gen Z?"
)

print(response.answer)
print(f"Sources: {len(response.document_sources)} documents cited")
```

#### Document Search & Retrieval
```python
# Hybrid search combining text and vector search
results = ds.documentstore.documents.search(
    query="consumer behavior trends 2024",
    extended_search=False
)

for result in results:
    print(f"📄 {result.artifact_title}")
    print(f"📝 {result.artifact_summary[:100]}...")
    print(f"📑 {len(result.page_references)} relevant pages\n")
```

#### User-Specific Document Management
```python
# Access documents through user permissions
uc = UserClient.get_userclient(
    "analyst@company.com",
    os.environ.get('MIP_API_KEY'),
    "https://api.deepsights.ai/ds/v1"
)

# List documents with user-specific access
total_docs, documents = uc.documents.documents_list(
    page_size=20,
    sort_field="creation_date",
    sort_order="DESC"
)

# Load specific documents with pages
loaded_docs = uc.documents.documents_load(
    document_ids=["doc_id_1", "doc_id_2"],
    load_pages=True
)

# Load specific document pages
pages = uc.documents.document_pages_load(["page_id_1", "page_id_2"])

# Hybrid search through user client
search_results = uc.documents.search(
    query="consumer behavior insights",
    extended_search=True
)
```

#### Topic Search with AI Analysis
```python
# AI-powered topic search available through user client
uc = UserClient.get_userclient(
    "analyst@company.com",
    os.environ.get('MIP_API_KEY'),
    "https://api.deepsights.ai/ds/v1"
)
results = uc.documents.topic_search(
    query="sustainable packaging trends",
    extended_search=True
)

for result in results:
    print(f"📄 {result.artifact_title}")
    print(f"📊 Relevance: {result.relevance_class}")
    print(f"📝 Summary: {result.artifact_summary[:100]}...")
    print(f"📑 {len(result.page_references)} relevant pages found\n")
```

#### Content Store Access
```python
# Search third-party content (requires CONTENTSTORE_API_KEY)
# News articles
news = ds.contentstore.news.search(
    query="sustainable packaging innovations",
    max_results=5
)
for item in news:
    print(f"{item.title} - {item.source}")

# Secondary reports
reports = ds.contentstore.secondary.search(
    query="sustainable packaging innovations",
    max_results=5
)
for item in reports:
    print(f"{item.title} - {item.source}")
```

#### Custom Taxonomy Management
```python
# Create a custom taxonomy for document classification
taxonomy = ds.documentstore.taxonomies.create(
    name="Product Categories",
    external_id="product-categories-v1"
)
print(f"Created taxonomy: {taxonomy.id}")

# Add a taxon type (classification level)
taxon_type = ds.documentstore.taxon_types.create(
    taxonomy_id=taxonomy.id,
    name="Category",
    description="Product category level"
)

# Add taxons (classification values)
parent_taxon = ds.documentstore.taxons.create(
    taxonomy_id=taxonomy.id,
    taxon_type_id=taxon_type.id,
    name="Electronics"
)

# Create child taxon with parent relationship
child_taxon = ds.documentstore.taxons.create(
    taxonomy_id=taxonomy.id,
    taxon_type_id=taxon_type.id,
    name="Smartphones",
    parent_ids=[parent_taxon.id]
)

# Search taxonomies
total, taxonomies = ds.documentstore.taxonomies.search(page_size=10)
for t in taxonomies:
    print(f"Taxonomy: {t.name} (status: {t.status})")

# Update a taxonomy
ds.documentstore.taxonomies.update(taxonomy.id, name="Updated Categories")

# Clean up (delete in reverse order: taxons, taxon types, taxonomy)
ds.documentstore.taxons.delete(child_taxon.id)
ds.documentstore.taxons.delete(parent_taxon.id)
ds.documentstore.taxon_types.delete(taxon_type.id)
ds.documentstore.taxonomies.delete(taxonomy.id)
```

#### Document Taxonomy Assignment
```python
from deepsights.documentstore.resources.documents import TaxonomyFilter

# Assign taxons to a document
ds.documentstore.documents.set_taxonomy(
    document_id="doc-id",
    taxonomy_id=taxonomy.id,
    taxon_ids=[taxon.id],
    excluded_taxon_ids=[]  # Optional: exclude specific taxons
)

# Get taxonomy assignments from a document
taxonomies = ds.documentstore.documents.get_taxonomies("doc-id")
for t in taxonomies:
    print(f"Taxonomy: {t.taxonomy_id}, Effective: {t.effective}")

# Clear taxonomy from a document
ds.documentstore.documents.clear_taxonomy("doc-id", taxonomy.id)

# Search with taxonomy filters
results = ds.documentstore.documents.search(
    query="consumer trends",
    taxonomy_filters=[TaxonomyFilter(field=taxonomy.id, values=[taxon.id])]
)
```

#### Error Handling & Rate Limiting
```python
import os
import time
import deepsights
from deepsights.userclient import UserClient

ds = deepsights.DeepSights()
uc = UserClient.get_userclient(
    "analyst@company.com",
    os.environ.get('MIP_API_KEY'),
    "https://api.deepsights.ai/ds/v1"
)

try:
    # Ask multiple questions - will demonstrate rate limiting
    for i in range(15):  # Exceeds 10/minute limit for answers
        response = uc.answersV2.create(f"Question {i}: Market trends?")
        print(f"✅ Question {i+1} processed")

except deepsights.RateLimitError as e:
    print(f"🚫 Rate limit exceeded: {e}")

    if e.retry_after:
        print(f"⏱️  Client-side limit - wait {e.retry_after} seconds")
        time.sleep(e.retry_after)
    else:
        print("⏱️  Server busy - try again later")

except deepsights.AuthenticationError as e:
    print(f"🔐 Authentication failed: {e}")

except deepsights.DeepSightsError as e:
    print(f"⚠️  API error: {e}")

# Alternative: Handle all rate limiting uniformly
try:
    response = uc.answersV2.create_and_wait("Your question here")

except deepsights.RateLimitError as e:
    # Handles both client-side (10/min) and server-side (persistent 429) limits
    print(f"Rate limit hit: {e}")

    # Implement your retry strategy
    if e.retry_after:
        time.sleep(e.retry_after)  # Known wait time
    else:
        time.sleep(60)  # Conservative fallback for server limits
```

All return values are [Pydantic objects](https://docs.pydantic.dev/latest/) with `.schema_human()` for exploring available properties. See [main.py](https://github.com/marketlogicsoftware/deepsights-api/blob/main/main.py) for more examples.


## Developer Information

### Pre-commit Hooks
- One-shot runner: `bash scripts/precommit.sh` (uses uv, loads `.env` if present, runs Ruff + Mypy + core tests, then validates hooks)
- Install hooks: `uv pip install pre-commit && pre-commit install`
- Run on all files: `pre-commit run --all-files`
- Hooks included: Ruff (lint + format), Mypy, core tests (`pytest -m "not heavy and not integration"`), plus basic whitespace/YAML checks.

Pytest markers
- `integration`: live API credentials + network required
- `heavy`: expensive operations (uploads, creating answers/reports)

Environment variables
- You can place credentials in a local `.env` at repo root; these are loaded automatically by tests and pre-commit (no need to export manually).

### UserClient Documents Capabilities
- Supported (end-user gateway): `documents.list`, `documents.load`, `documents.load_pages`, `documents.search` (hybrid), `documents.download`.
- Not available via user token: `documents.upload`, `documents.wait_for_upload`, `documents.delete`, `documents.wait_for_delete`, `documents.search_documents`, `documents.search_pages`.
- Notes: Page text for userclient is returned directly by the API (lightly normalized); docstore adds segmentation on page content.

### Rate Limits & Error Handling

The DeepSights API implements **comprehensive rate limiting** to ensure fair usage and optimal performance:

#### Client-Side Rate Limits
- **AI Answers**: 10 requests per 60 seconds (`uc.answersV2.create()`)
- **AI Reports**: 3 requests per 60 seconds (`uc.reports.create()`)
- **General GET requests**: 1,000 per 60 seconds
- **General POST requests**: 100 per 60 seconds

#### Behavior
- **Client-side limits**: Immediate `RateLimitError` with `retry_after` information
- **Server-side limits**: Automatic retry with exponential backoff (up to 3 attempts)
- **Persistent server limits**: Convert to `RateLimitError` after retries for consistent handling

#### Exception Hierarchy
```python
deepsights.DeepSightsError          # Base exception
├── deepsights.RateLimitError       # Rate limiting (client + server)
└── deepsights.AuthenticationError  # Invalid API keys/permissions
```

#### Best Practices
```python
# Recommended error handling pattern
try:
    response = uc.answersV2.create_and_wait("Your question")

except deepsights.RateLimitError as e:
    # Single handler for all rate limiting scenarios
    wait_time = e.retry_after or 60  # Use provided time or conservative fallback
    print(f"Rate limited, waiting {wait_time} seconds...")
    time.sleep(wait_time)

except deepsights.AuthenticationError:
    print("Check your API keys and permissions")
```

### Caching
- User client responses cached for 240 seconds (TTL)
- Document search results intelligently cached
- Reduces API calls and improves performance

### Authentication
DeepSights supports multiple authentication methods:
- **API Key**: Primary authentication (set `DEEPSIGHTS_API_KEY`)
- **OAuth Token**: Enterprise integration support
- **Service-specific keys**: Optional keys for ContentStore and MIP access
- **Unified Token**: Bearer token with automatic refresh on 401 (for ContentStore and UserClient)

#### Unified Token Authentication
For scenarios requiring custom token management (e.g., integrating with external auth systems), ContentStore and UserClient support unified token authentication with automatic refresh:

```python
from deepsights.contentstore import ContentStore
from deepsights.userclient import UserClient

def my_refresh_callback():
    # Your logic to obtain a new token (must implement timeout!)
    new_token = get_token_from_auth_server(timeout=10)
    return new_token  # Return None to signal permanent auth failure

# ContentStore with unified token
cs = ContentStore.with_unified_token(
    unified_token="your_bearer_token",
    refresh_callback=my_refresh_callback
)

# UserClient with unified token
uc = UserClient.with_unified_token(
    unified_token="your_bearer_token",
    refresh_callback=my_refresh_callback
)
```

The unified token mode automatically refreshes the token on 401 responses (up to 2 attempts) and is thread-safe for multi-threaded applications.

### Response Format
All API responses are strongly-typed [Pydantic models](https://docs.pydantic.dev/latest/) with:
```python
# Explore available properties
print(response.schema_human())

# Access nested data with IDE autocomplete
answer_text = response.answer
source_count = len(response.sources)
```

## Documentation & Support

- **API Documentation**: [GitHub Pages](https://marketlogicsoftware.github.io/deepsights-api/)
- **Issues & Support**: [GitHub Issues](https://github.com/marketlogicsoftware/deepsights-api/issues)
- **API Portal**: [DeepSights API Portal](https://apiportal.mlsdevcloud.com/deep-sights)


## License

This project is licensed under the Apache 2.0 License - see the [LICENSE](LICENSE) file for details.
## Testing

- Unit tests (offline):
  - Run without credentials: `pytest -m "not integration"`
  - These tests rely on mocks and do not perform network calls.

- Integration tests (live APIs):
  - Export required credentials: `DEEPSIGHTS_API_KEY`, `MIP_API_KEY`, `MIP_IDENTITY_VALID_EMAIL`
  - Or set `DEEPSIGHTS_RUN_INTEGRATION=1` to enable integration fixtures.
  - Run integration tests: `pytest -m integration`
