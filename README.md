# 🤖💡 deepsights-api 

[![PyPI](https://img.shields.io/pypi/v/deepsights-api.svg)](https://pypi.org/project/deepsights-api/) [![Changelog](https://img.shields.io/github/v/release/marketlogicsoftware/deepsights-api?include_prereleases&label=changelog)](https://github.com/marketlogicsoftware/deepsights-api/releases) [![Tests](https://img.shields.io/github/actions/workflow/status/marketlogicsoftware/deepsights-api/run_tests.yml)](https://github.com/marketlogicsoftware/deepsights-api/actions/workflows/run_tests.yml) [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/marketlogicsoftware/deepsights-api/blob/main/LICENSE)

This is the official Python client library for the [DeepSights API](https://apiportal.mlsdevcloud.com/deep-sights). 

The library has been built and tested on Python 3.10 - 3.12. Please channel any feedback or issues via the [github page](https://github.com/marketlogicsoftware/deepsights-api). 

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


### Hello, world

To retrieve an answer from DeepSights:

```Python
import deepsights

# with API keys from environment
ds = deepsights.DeepSights()

# obtain the user client; you will need an actual user's email here!
uc = ds.get_userclient("john.doe@acme.com")

# obtain an answer
response = uc.answersV2.create_and_wait("What are emerging food consumption moments for Gen Z?")

# returned data are pydantic objects
print(response.answer)

# you can retrieve the supported properties via schema_human()
print(response.schema_human())
```

See [main.py](https://github.com/marketlogicsoftware/deepsights-api/blob/main/main.py) for more examples. Note that all non-trivial return value from DeepSights API functions are [pydantic objects](https://docs.pydantic.dev/latest/).


## Documentation

Access the [documentation on github](https://marketlogicsoftware.github.io/deepsights-api/).
