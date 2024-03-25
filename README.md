# 🤖💡 deepsights-api 

[![PyPI](https://img.shields.io/pypi/v/deepsights-api.svg)](https://pypi.org/project/deepsights-api/) [![Changelog](https://img.shields.io/github/v/release/marketlogicsoftware/deepsights-api?include_prereleases&label=changelog)](https://github.com/marketlogicsoftware/deepsights-api/releases) [![Tests](https://img.shields.io/github/actions/workflow/status/marketlogicsoftware/deepsights-api/run_tests.yml)](https://github.com/marketlogicsoftware/deepsights-api/actions/workflows/run_tests.yml) [![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/marketlogicsoftware/deepsights-api/blob/main/LICENSE)

This is the official Python client library for the [DeepSights API](https://apiportal.mlsdevcloud.com/deep-sights). Please channel any feedback or issues via the [official github page](https://github.com/marketlogicsoftware/deepsights-api). 

`deepsights-api` supports access to the DeepSights API for retrieving answers and reports, as well as searching and managing internal documents. It also supports the ContentStore API for direct searching of news articles and secondary reports.

The library has been built and tested on Python 3.10 - 3.12.

## Getting started

### Installation

Install this library using `pip`; we recommend installing it in a [virtualenv](https://virtualenv.pypa.io/en/latest/).

```shell
pip install deepsights-api
```

### API keys

[Contact us](https://apiportal.mlsdevcloud.com/get-started#Get_API_key) to obtain your API key (may require commercial add-on). **Note that your API key may be authorized to access only a subset of the API endpoints.** 

Configure your api keys either in your environment, or provide it as an argument to the API constructor.

```shell
DEEPSIGHTS_API_KEY = <your DeepSights API key>
CONTENTSTORE_API_KEY = <your ContentStore API key; optional>
```

then 

```Python
import deepsights

# with keys from environment
ds = deepsights.DeepSights()
cs = deepsights.ContentStore()

# with explicit key
ds = deepsights.DeepSights(api_key="<your API key>")
cs = deepsights.ContentStore(api_key="<your API key>")
```


### Hello, world

To retrieve an answer from DeepSights:

```Python
import deepsights

# with API keys from environment
ds = deepsights.DeepSights()

# obtain answer
response = ds.answers.create_and_wait(ds, "What are emerging food consumption moments for Gen Z?")

# returned data are pydantic objects
print(response.answers[0].answer)

# you can retrieve the supported properties via schema_human()
print(response.schema_human())
```

See [main.py](https://github.com/marketlogicsoftware/deepsights-api/blob/main/main.py) for more examples. Note that all non-trivial return value from DeepSights API functions are [pydantic objects](https://docs.pydantic.dev/latest/).


## Documentation

Access the [documentation on github](https://marketlogicsoftware.github.io/deepsights-api/).
