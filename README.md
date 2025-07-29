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

The **Document Store** hosts all customer-owned documents, such as presentations and reports. The `documentstore` API exposes lifecycle management, search and access to documents.

### Content Store

The **Content Store** holds public and paid 3rd party content, including industry news and secondary sources. The `contentstore` API exposes search and access to this content.

### User Client

The **User Client** serves to impersonate existing platform users with their access permissions. The `userclient` API supports obtaining AI-generated answers and reports in response to business questions, as well as document management operations with user-specific permissions including document listing, loading, page access, hybrid search, and topic search capabilities.


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
results = uc.search.search(
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
content = ds.contentstore.content.search(
    query="sustainable packaging innovations",
    limit=5
)

for item in content.results:
    print(f"{item.title} - {item.source}")
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
