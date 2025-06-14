# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Development Commands

### Testing
- `pytest` - Run all tests
- `pytest tests/documentstore/` - Run specific test module
- `pytest -v` - Run tests with verbose output

### Code Quality
- `pylint $(git ls-files '*.py')` - Run linting on all Python files
- `pip install uv && uv pip install --system ".[lint]"` - Install linting dependencies

### Documentation
- `pip install uv && uv pip install --system ".[docs]"` - Install documentation dependencies
- `pdoc deepsights` - Generate API documentation

### Development Setup
- `pip install uv && uv pip install --system ".[test]"` - Install with test dependencies
- `pip install -e .` - Install in development mode

## Architecture Overview

This is a Python client library for the DeepSights API that provides unified access to three main services through a hierarchical resource pattern:

```
DeepSights (main client)
├── documentstore - Customer document lifecycle management
├── contentstore - Public/paid 3rd party content access
├── userclient - AI-generated answers via user impersonation
└── quota - API usage tracking
```

### Core Components

**Authentication**: Dual system supporting API keys and OAuth tokens via base classes `APIKeyAPI` and `OAuthTokenAPI` in `deepsights/api/`.

**Resource Pattern**: Each service follows consistent resource structure extending base API clients with dependency injection.

**Models**: All API responses are typed Pydantic models extending `DeepSightsBaseModel` for human-readable schemas.

**Caching**: TTL-based caching (240s for user clients) using `cachetools` with sophisticated document caching in `documentstore`.

**Rate Limiting**: Built-in limits (1000 GET, 100 POST per 60s) with exponential backoff retry logic via `tenacity`.

### Key Features

**Search & Retrieval**: Vector-based document search with embeddings, hybrid search combining text/vector results, and recency weighting algorithms.

**Document Management**: Complete lifecycle (upload/search/download/delete) with page-level search and batch operations.

**AI Integration**: User impersonation for AI answers and report generation with permission-based access control.

## Environment Configuration

Required API keys (set in environment or pass to constructor):
- `DEEPSIGHTS_API_KEY` - Core API access
- `CONTENTSTORE_API_KEY` - Content store access (optional)
- `MIP_API_KEY` - User client functionality (optional)
- `MIP_IDENTITY_VALID_EMAIL` - Valid user email for testing

## Testing Structure

Tests mirror source structure with integration tests for each service. Test data includes JSON, PDF, and text files in `tests/data/`. Environment-based API key configuration supports CI/CD workflows.