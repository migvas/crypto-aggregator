# Test Suite Documentation

This directory contains comprehensive unit tests for the Crypto Price Aggregator API.

## Test Structure

### `test_providers.py`
Tests for individual provider classes with mocked external API calls:
- **TestCoinGecko**: Tests for CoinGecko provider
  - Symbol to coin ID conversion
  - Synchronous and asynchronous price fetching
  - Data normalization
- **TestBinance**: Tests for Binance provider
  - Symbol to trading pair conversion
  - Synchronous and asynchronous price fetching
  - Data normalization
- **TestCoinbase**: Tests for Coinbase provider
  - Synchronous and asynchronous price fetching
  - Data normalization

### `test_aggregator.py`
Tests for the ProviderAggregator logic:
- **TestProviderAggregator**: Tests for aggregator functionality
  - Synchronous price fetching from multiple providers
  - Asynchronous price fetching with error handling (timeout, HTTP errors, generic exceptions)
  - Data normalization across multiple providers
  - Average price calculation and rounding
  - Provider factory function

### `test_main.py`
Tests for FastAPI endpoints:
- **TestGetPrices**: Tests for `/prices` endpoint
  - Successful price fetching
  - Multiple symbol handling
  - Whitespace and case handling
  - Error handling (no symbols, missing parameters, no data)
- **TestAsyncGetPrices**: Tests for `/async_prices` endpoint
  - Async price fetching
  - Error handling
  - Provider failure resilience
- **TestModels**: Tests for Pydantic models

## Running Tests

### Run all tests:
```bash
pytest tests/
```

### Run with verbose output:
```bash
pytest tests/ -v
```

### Run specific test file:
```bash
pytest tests/test_providers.py -v
```

### Run specific test class:
```bash
pytest tests/test_providers.py::TestCoinGecko -v
```

### Run specific test:
```bash
pytest tests/test_providers.py::TestCoinGecko::test_fetch_success -v
```

### Run with coverage:
```bash
pytest tests/ --cov=app --cov-report=html
```

## Key Features

- **External API Mocking**: All external API calls are mocked using `unittest.mock`
- **Async Support**: Tests include both synchronous and asynchronous code paths
- **Error Handling**: Comprehensive error scenario testing
- **Isolated Tests**: Each test is independent and doesn't rely on external services

## Test Count

- **37 total tests**
- Provider tests: 11
- Aggregator tests: 10
- API endpoint tests: 14
- Model tests: 2

## Dependencies

- `pytest`: Test framework
- `pytest-asyncio`: Async test support
- `unittest.mock`: Mocking external dependencies
- `fastapi.testclient`: Testing FastAPI endpoints
