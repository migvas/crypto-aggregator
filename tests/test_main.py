"""Unit tests for FastAPI endpoints with mocked aggregator."""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch, AsyncMock
from app.main import app


@pytest.fixture
def client():
    """Create a test client for the FastAPI app."""
    return TestClient(app)


@pytest.fixture
def mock_aggregator():
    """Create a mock ProviderAggregator."""
    mock = Mock()
    return mock


class TestGetPrices:
    """Test the /prices endpoint."""

    @patch('app.main.pagg')
    def test_get_prices_success(self, mock_pagg, client):
        """Test successful price fetch."""
        mock_pagg.fetch_prices.return_value = {
            "provider1": {"data": {}},
            "provider2": {"data": {}}
        }
        mock_pagg.normalize_data.return_value = {
            "BTC": {
                "avg_price": 50000.0,
                "results": 2,
                "sources": {"provider1": 50000.0, "provider2": 50000.0}
            }
        }

        response = client.get("/prices?q=BTC")

        assert response.status_code == 200
        data = response.json()
        assert "symbols" in data
        assert "BTC" in data["symbols"]
        assert data["symbols"]["BTC"]["avg_price"] == 50000.0
        assert data["symbols"]["BTC"]["results"] == 2

    @patch('app.main.pagg')
    def test_get_prices_multiple_symbols(self, mock_pagg, client):
        """Test fetching multiple symbols."""
        mock_pagg.fetch_prices.return_value = {
            "provider1": {"data": {}}
        }
        mock_pagg.normalize_data.return_value = {
            "BTC": {
                "avg_price": 50000.0,
                "results": 1,
                "sources": {"provider1": 50000.0}
            },
            "ETH": {
                "avg_price": 3000.0,
                "results": 1,
                "sources": {"provider1": 3000.0}
            }
        }

        response = client.get("/prices?q=BTC,ETH")

        assert response.status_code == 200
        data = response.json()
        assert "BTC" in data["symbols"]
        assert "ETH" in data["symbols"]
        mock_pagg.fetch_prices.assert_called_once_with(["BTC", "ETH"])

    @patch('app.main.pagg')
    def test_get_prices_whitespace_handling(self, mock_pagg, client):
        """Test that whitespace in query is handled correctly."""
        mock_pagg.fetch_prices.return_value = {"provider1": {"data": {}}}
        mock_pagg.normalize_data.return_value = {
            "BTC": {
                "avg_price": 50000.0,
                "results": 1,
                "sources": {"provider1": 50000.0}
            }
        }

        response = client.get("/prices?q=BTC, ETH , SOL")

        assert response.status_code == 200
        mock_pagg.fetch_prices.assert_called_once_with(["BTC", "ETH", "SOL"])

    def test_get_prices_no_symbols(self, client):
        """Test error when no symbols provided."""
        response = client.get("/prices?q=")

        assert response.status_code == 400
        assert "No symbols provided" in response.json()["detail"]

    def test_get_prices_missing_query_param(self, client):
        """Test error when query parameter is missing."""
        response = client.get("/prices")

        assert response.status_code == 422  # FastAPI validation error

    @patch('app.main.pagg')
    def test_get_prices_no_data_from_providers(self, mock_pagg, client):
        """Test error when no provider returns data."""
        mock_pagg.fetch_prices.return_value = {"provider1": {"data": {}}}
        mock_pagg.normalize_data.return_value = {}

        response = client.get("/prices?q=BTC")

        assert response.status_code == 503
        assert "No data available" in response.json()["detail"]

    @patch('app.main.pagg')
    def test_get_prices_case_insensitive(self, mock_pagg, client):
        """Test that symbols are converted to uppercase."""
        mock_pagg.fetch_prices.return_value = {"provider1": {"data": {}}}
        mock_pagg.normalize_data.return_value = {
            "BTC": {
                "avg_price": 50000.0,
                "results": 1,
                "sources": {"provider1": 50000.0}
            }
        }

        response = client.get("/prices?q=btc")

        assert response.status_code == 200
        mock_pagg.fetch_prices.assert_called_once_with(["BTC"])


class TestAsyncGetPrices:
    """Test the /async_prices endpoint."""

    @pytest.mark.asyncio
    @patch('app.main.pagg')
    async def test_async_get_prices_success(self, mock_pagg, client):
        """Test successful async price fetch."""
        mock_pagg.afetch_prices = AsyncMock(return_value={
            "provider1": {"ok": True, "data": {}},
            "provider2": {"ok": True, "data": {}}
        })
        mock_pagg.normalize_data.return_value = {
            "BTC": {
                "avg_price": 50000.0,
                "results": 2,
                "sources": {"provider1": 50000.0, "provider2": 50000.0}
            }
        }

        response = client.get("/async_prices?q=BTC")

        assert response.status_code == 200
        data = response.json()
        assert "symbols" in data
        assert "BTC" in data["symbols"]
        assert data["symbols"]["BTC"]["avg_price"] == 50000.0

    @pytest.mark.asyncio
    @patch('app.main.pagg')
    async def test_async_get_prices_multiple_symbols(self, mock_pagg, client):
        """Test async fetching multiple symbols."""
        mock_pagg.afetch_prices = AsyncMock(return_value={
            "provider1": {"ok": True, "data": {}}
        })
        mock_pagg.normalize_data.return_value = {
            "BTC": {
                "avg_price": 50000.0,
                "results": 1,
                "sources": {"provider1": 50000.0}
            },
            "ETH": {
                "avg_price": 3000.0,
                "results": 1,
                "sources": {"provider1": 3000.0}
            }
        }

        response = client.get("/async_prices?q=BTC,ETH")

        assert response.status_code == 200
        data = response.json()
        assert "BTC" in data["symbols"]
        assert "ETH" in data["symbols"]

    def test_async_get_prices_no_symbols(self, client):
        """Test async endpoint error when no symbols provided."""
        response = client.get("/async_prices?q=")

        assert response.status_code == 400
        assert "No symbols provided" in response.json()["detail"]

    def test_async_get_prices_missing_query_param(self, client):
        """Test async endpoint error when query parameter is missing."""
        response = client.get("/async_prices")

        assert response.status_code == 422

    @pytest.mark.asyncio
    @patch('app.main.pagg')
    async def test_async_get_prices_no_data(self, mock_pagg, client):
        """Test async endpoint error when no provider returns data."""
        mock_pagg.afetch_prices = AsyncMock(return_value={
            "provider1": {"ok": True, "data": {}}
        })
        mock_pagg.normalize_data.return_value = {}

        response = client.get("/async_prices?q=BTC")

        assert response.status_code == 503
        assert "No data available" in response.json()["detail"]

    @pytest.mark.asyncio
    @patch('app.main.pagg')
    async def test_async_get_prices_with_provider_failures(self, mock_pagg, client):
        """Test async endpoint handles provider failures gracefully."""
        mock_pagg.afetch_prices = AsyncMock(return_value={
            "provider1": {"ok": True, "data": {}},
            "provider2": {"ok": False, "error": "timeout"}
        })
        mock_pagg.normalize_data.return_value = {
            "BTC": {
                "avg_price": 50000.0,
                "results": 1,
                "sources": {"provider1": 50000.0}
            }
        }

        response = client.get("/async_prices?q=BTC")

        assert response.status_code == 200
        data = response.json()
        assert "BTC" in data["symbols"]
        # Only one source since provider2 failed
        assert data["symbols"]["BTC"]["results"] == 1


class TestModels:
    """Test Pydantic models."""

    def test_symbol_view_creation(self):
        """Test creating SymbolView model."""
        from app.models import SymbolView
        
        symbol = SymbolView(
            avg_price=50000.0,
            results=2,
            sources={"provider1": 50000.0, "provider2": 51000.0}
        )
        
        assert symbol.avg_price == 50000.0
        assert symbol.results == 2
        assert len(symbol.sources) == 2

    def test_price_response_creation(self):
        """Test creating PriceResponse model."""
        from app.models import PriceResponse, SymbolView
        
        response = PriceResponse(
            symbols={
                "BTC": SymbolView(
                    avg_price=50000.0,
                    results=1,
                    sources={"provider1": 50000.0}
                )
            }
        )
        
        assert "BTC" in response.symbols
        assert response.symbols["BTC"].avg_price == 50000.0
