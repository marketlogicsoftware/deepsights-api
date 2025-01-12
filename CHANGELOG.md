# Changelog

<!--next-version-placeholder-->

## v1.2.2 (12-Jan-2025)

- Add AI generated title to model 


## v1.2.1 (04-Oct-2024)

- Fix for concurrency issue in document loading


## v1.2.0 (02-Oct-2024)

- Compatibility with visual extraction
- Removed answers V1 


## v1.1.1 (09-Sep-2024)

- Force contentstore search to retrieve only AI eligible content 

## v1.1.0 (16-Aug-2024)

- Deprecating answer endpoint, replacing with answersV2

## v1.0.4 (05-Jun-2024)

- Added match paragraphs results for contentstore search


## v1.0.3 (30-May-2024)

- Added time filters for content store text & vector search


## v1.0.2 (15-May-2024)

- Added language filtering for search
- Expose text and vector search for content store


## v1.0.1 (14-May-2024)

- Added date range filtering for content store searches


## v1.0.0 (26-Mar-2024)

- Introduced user client, removing answers and reports from API key based super-access
- Restructured API clients to use API resources for improved modularity
- Retried sync answers v1
- Support for new hybrid SCS endpoint
- Introduced documents.list() method
- Added creation_date to document model
- Quality of life improvements to documents.download()


## v0.2.0 (01-Mar-2024)

- First public release of `deepsights-api`
