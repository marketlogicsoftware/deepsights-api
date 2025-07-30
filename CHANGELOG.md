# Changelog

<!--next-version-placeholder-->

## v1.3.9 (30-Jul-2025)

- Consistent DocumentResource methods for user client and deepsights B2B client

## v1.3.8 (29-Jul-2025)

- User client refactoring for use w/o B2B DS key

## v1.3.7 (29-Jul-2025)

- Custom endpoint support

## v1.3.6 (24-Jul-2025)

- Support document page retrieval via user token endpoints 

## v1.3.5 (11-Jul-2025)

- Add configurable endpoint base URL for test envs

## v1.3.4 (11-Jul-2025)

- Extended hybrid search query length limitation to 512 chars

## v1.3.3 (26-Jun-2025)

- Auto-refresh token for userclient
- Streamlined rate limiting and error handling
 

## v1.3.2 (18-Jun-2025)

- Improved error logging for answer polling
- Documentation fix

## v1.3.1 (17-Jun-2025)

- **BREAKING CHANGE**: Removed topic_search from documentstore (moved to userclient only)
- Added comprehensive userclient document management: documents_list(), documents_load(), document_pages_load()
- Enhanced userclient with hybrid_search functionality
- Topic search models moved from documentstore to userclient.topic_search module
- Deprecated documentstore.search_documents() in favor of documentsearch.hybrid_search()
- Added extensive test coverage for new userclient document methods
- Clean up of packaging

## v1.3.0 (15-Jun-2025)

- Added topic-search & hybrid-search support for documentstore and userclient
- Added support evidence filtering to content store; removed exact match promotion
- Enhanced API client with robust error handling, retry logic for 429/502/503 status codes, and connection pooling
- Added configurable timeouts, debug logging, and expanded HTTP success code support
- Improved utils package with thread-safe caching, order-preserving parallel execution, and enhanced error handling
- Optimized ranking algorithms
- Exposed `search_only_ai_allowed_content` parameter in all contentstore search methods for full content access control
- Fixed security vulnerabilities in documentstore
- Refactored userclient polling logic with shared utility and improved error handling
- Added tenacity retry patterns and safe dictionary access to userclient resources


## v1.2.4 (16-Apr-2025)

- Sort order in SCS text search

## v1.2.3 (25-Jan-2025)

- Support item text download from cont

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
