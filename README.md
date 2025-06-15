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

The **User Client** serves to impersonate existing platform users with their access permissions. The `userclient` API supports obtaining AI-generated answers and reports in reponse to business questions.


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
import deepsights

# Initialize with API keys from environment
ds = deepsights.DeepSights()

# Get user client for AI-generated insights
uc = ds.get_userclient("analyst@company.com")

# Ask business questions and get AI answers
response = uc.answersV2.create_and_wait(
    "What are emerging food consumption moments for Gen Z?"
)

print(response.answer)
print(f"Sources: {len(response.sources)} documents cited")
```

#### Document Search & Retrieval
```python
# Search your document store
documents = ds.documentstore.documents.search(
    query="consumer behavior trends 2024",
    limit=10
)

for doc in documents.results:
    print(f"{doc.title} - {doc.upload_date}")
```

#### Topic Search with AI Analysis
```python
# AI-powered topic search for comprehensive insights
results = ds.documentstore.documents.topic_search(
    query="sustainable packaging trends", 
    extended_search=True
)

for result in results:
    print(f"📄 {result.artifact_title}")
    print(f"📊 Relevance: {result.relevance_class}")
    print(f"📝 Summary: {result.artifact_summary[:100]}...")
    print(f"📑 {len(result.page_references)} relevant pages found\n")

# User client version with OAuth authentication
uc = ds.get_userclient("analyst@company.com") 
user_results = uc.topic_search.search("market disruption AI")
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

#### Error Handling
```python
try:
    response = uc.answersV2.create_and_wait("Your question here")
except deepsights.exceptions.AuthenticationError:
    print("Invalid API key or permissions")
except deepsights.exceptions.RateLimitError:
    print("Rate limit exceeded - please wait")
```

All return values are [Pydantic objects](https://docs.pydantic.dev/latest/) with `.schema_human()` for exploring available properties. See [main.py](https://github.com/marketlogicsoftware/deepsights-api/blob/main/main.py) for more examples.


## Developer Information

### Rate Limits
- **GET requests**: 1,000 per 60 seconds
- **POST requests**: 100 per 60 seconds
- Automatic exponential backoff retry logic included

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
