# Crypto Price Aggregator

A FastAPI-based cryptocurrency price aggregation service that fetches real-time price data from multiple providers and returns normalized, averaged results.

## Features

- **Fast API**: Built with FastAPI for high performance and automatic API documentation
- **Multi-Provider Support**: Aggregates data from multiple cryptocurrency exchanges
- **Async & Sync**: Supports both synchronous and asynchronous price fetching
- **Price Averaging**: Calculates average prices across multiple data sources
- **Error Handling**: Robust error handling for provider failures
- **Auto Documentation**: Interactive API docs available at `/docs`

## Supported Providers

- **Coinbase**: Coinbase Pro/Advanced Trade API
- **Binance**: Binance public API
- **CoinGecko**: CoinGecko public API

## Installation

This project uses [uv](https://github.com/astral-sh/uv) for dependency management.

1. Clone the repository:
   ```bash
   git clone <your-repo-url>
   cd crypto-aggregator
   ```

2. Install dependencies:
   ```bash
   uv sync
   ```

3. Run the application:
   ```bash
   uv run fastapi dev app/main.py
   ```

The API will be available at `http://localhost:8000`

## API Endpoints

### GET /prices

Fetch cryptocurrency prices synchronously.

**Parameters:**
- `q` (query parameter): Comma-separated list of cryptocurrency symbols (e.g., "BTC,ETH,ADA")

**Example:**
```bash
curl "http://localhost:8000/prices?q=BTC,ETH"
```

**Response:**
```json
{
  "symbols": {
    "BTC": {
      "avg_price": 45000.50,
      "results": 3,
      "sources": {
        "coinbase": 45010.25,
        "binance": 44995.75,
        "coingecko": 44995.50
      }
    },
    "ETH": {
      "avg_price": 3200.33,
      "results": 3,
      "sources": {
        "coinbase": 3205.50,
        "binance": 3198.25,
        "coingecko": 3197.25
      }
    }
  }
}
```

### GET /async_prices

Fetch cryptocurrency prices asynchronously for better performance.

**Parameters:**
- `q` (query parameter): Comma-separated list of cryptocurrency symbols

**Example:**
```bash
curl "http://localhost:8000/async_prices?q=BTC,ETH,SOL"
```

Respo
nse format is identical to the `/prices` endpoint.

## Response Schema

### SymbolView
- `avg_price`: Average price across all successful provider responses
- `results`: Number of providers that successfully returned data
- `sources`: Object mapping provider names to their reported prices

### PriceResponse
- `symbols`: Object mapping cryptocurrency symbols to their SymbolView data

## Development

### Project Structure
```
crypto-aggregator/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application and routes
│   ├── models.py            # Pydantic data models
│   ├── provider_aggregator.py # Core aggregation logic
│   └── providers/           # Individual provider implementations
│       ├── __init__.py
│       ├── binance.py
│       ├── coin_gecko.py
│       └── coinbase.py
├── pyproject.toml           # Project configuration
└── README.md
```

### Adding New Providers

To add a new cryptocurrency data provider:

1. Create a new file in `app/providers/`
2. Implement the provider class with required methods:
   - `fetch(symbols)`: Synchronous data fetching
   - `afetch(symbols, client)`: Asynchronous data fetching
   - `normalize_data(raw_data)`: Data normalization
3. Add the provider to the aggregator in `provider_aggregator.py`

## API Documentation

When the application is running, you can access:
- **Interactive API docs**: http://localhost:8000/docs
- **ReDoc documentation**: http://localhost:8000/redoc

## Testing

This project includes a comprehensive test suite.

### Running Tests

Run all tests:
```bash
pytest tests/
```

Run tests with verbose output:
```bash
pytest tests/ -v
```

Run tests with coverage report:
```bash
pytest tests/ --cov=app --cov-report=term-missing
```

Generate HTML coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
# Open htmlcov/index.html in your browser
```

### Test Structure

- **`tests/test_providers.py`**: Unit tests for individual provider classes (CoinGecko, Binance, Coinbase)
- **`tests/test_aggregator.py`**: Tests for the ProviderAggregator logic and data normalization
- **`tests/test_main.py`**: Tests for FastAPI endpoints and request handling

For more details, see [`tests/README.md`](tests/README.md).

## Requirements

- Python >= 3.12
- FastAPI
- httpx (for async HTTP requests)
- requests (for sync HTTP requests)
- pytest (for testing)
- pytest-asyncio (for async tests)
- pytest-cov (for coverage reports)
