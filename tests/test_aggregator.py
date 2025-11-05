"""Unit tests for ProviderAggregator with mocked providers."""
import pytest
from unittest.mock import Mock, AsyncMock, patch
import httpx
from app.provider_aggregator import ProviderAggregator, build_providers


class TestProviderAggregator:
    """Test ProviderAggregator logic."""

    def test_fetch_prices(self):
        """Test synchronous fetch_prices aggregation."""
        # Create mock providers
        mock_provider1 = Mock()
        mock_provider1.name = "provider1"
        mock_provider1.fetch.return_value = {"BTC": 50000.0}

        mock_provider2 = Mock()
        mock_provider2.name = "provider2"
        mock_provider2.fetch.return_value = {"BTC": 51000.0}

        aggregator = ProviderAggregator([mock_provider1, mock_provider2])
        result = aggregator.fetch_prices(["BTC"])

        assert result == {
            "provider1": {"BTC": 50000.0},
            "provider2": {"BTC": 51000.0}
        }
        mock_provider1.fetch.assert_called_once_with(symbols=["BTC"])
        mock_provider2.fetch.assert_called_once_with(symbols=["BTC"])

    @pytest.mark.asyncio
    async def test_afetch_prices_success(self):
        """Test async fetch_prices with successful responses."""
        # Create mock providers
        mock_provider1 = Mock()
        mock_provider1.name = "provider1"
        mock_provider1.afetch = AsyncMock(return_value={"BTC": 50000.0})

        mock_provider2 = Mock()
        mock_provider2.name = "provider2"
        mock_provider2.afetch = AsyncMock(return_value={"BTC": 51000.0})

        aggregator = ProviderAggregator([mock_provider1, mock_provider2])
        
        with patch('app.provider_aggregator.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await aggregator.afetch_prices(["BTC"])

        assert result == {
            "provider1": {"ok": True, "data": {"BTC": 50000.0}},
            "provider2": {"ok": True, "data": {"BTC": 51000.0}}
        }

    @pytest.mark.asyncio
    async def test_afetch_prices_with_timeout(self):
        """Test async fetch_prices when provider times out."""
        mock_provider1 = Mock()
        mock_provider1.name = "provider1"
        mock_provider1.afetch = AsyncMock(return_value={"BTC": 50000.0})

        mock_provider2 = Mock()
        mock_provider2.name = "provider2"
        mock_provider2.afetch = AsyncMock(side_effect=httpx.TimeoutException("Timeout"))

        aggregator = ProviderAggregator([mock_provider1, mock_provider2])
        
        with patch('app.provider_aggregator.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await aggregator.afetch_prices(["BTC"])

        assert result["provider1"]["ok"] is True
        assert result["provider2"]["ok"] is False
        assert result["provider2"]["error"] == "timeout"

    @pytest.mark.asyncio
    async def test_afetch_prices_with_http_error(self):
        """Test async fetch_prices when provider returns HTTP error."""
        mock_provider1 = Mock()
        mock_provider1.name = "provider1"
        mock_provider1.afetch = AsyncMock(return_value={"BTC": 50000.0})

        mock_provider2 = Mock()
        mock_provider2.name = "provider2"
        mock_response = Mock()
        mock_response.status_code = 500
        http_error = httpx.HTTPStatusError("Server error", request=Mock(), response=mock_response)
        mock_provider2.afetch = AsyncMock(side_effect=http_error)

        aggregator = ProviderAggregator([mock_provider1, mock_provider2])
        
        with patch('app.provider_aggregator.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await aggregator.afetch_prices(["BTC"])

        assert result["provider1"]["ok"] is True
        assert result["provider2"]["ok"] is False
        assert result["provider2"]["error"] == "http 500"

    @pytest.mark.asyncio
    async def test_afetch_prices_with_generic_exception(self):
        """Test async fetch_prices when provider raises generic exception."""
        mock_provider1 = Mock()
        mock_provider1.name = "provider1"
        mock_provider1.afetch = AsyncMock(return_value={"BTC": 50000.0})

        mock_provider2 = Mock()
        mock_provider2.name = "provider2"
        mock_provider2.afetch = AsyncMock(side_effect=Exception("Generic error"))

        aggregator = ProviderAggregator([mock_provider1, mock_provider2])
        
        with patch('app.provider_aggregator.httpx.AsyncClient') as mock_client_class:
            mock_client = AsyncMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            
            result = await aggregator.afetch_prices(["BTC"])

        assert result["provider1"]["ok"] is True
        assert result["provider2"]["ok"] is False
        assert result["provider2"]["error"] == "Generic error"

    def test_normalize_data_single_provider(self):
        """Test normalize_data with single provider."""
        mock_provider = Mock()
        mock_provider.name = "provider1"
        mock_provider.normalize_data.return_value = {"BTC": 50000.0, "ETH": 3000.0}

        aggregator = ProviderAggregator([mock_provider])
        raw_data = {
            "provider1": {"data": {"some": "data"}}
        }
        
        result = aggregator.normalize_data(raw_data)

        assert result == {
            "BTC": {
                "results": 1,
                "avg_price": 50000.0,
                "sources": {"provider1": 50000.0}
            },
            "ETH": {
                "results": 1,
                "avg_price": 3000.0,
                "sources": {"provider1": 3000.0}
            }
        }

    def test_normalize_data_multiple_providers(self):
        """Test normalize_data with multiple providers."""
        mock_provider1 = Mock()
        mock_provider1.name = "provider1"
        mock_provider1.normalize_data.return_value = {"BTC": 50000.0}

        mock_provider2 = Mock()
        mock_provider2.name = "provider2"
        mock_provider2.normalize_data.return_value = {"BTC": 51000.0}

        mock_provider3 = Mock()
        mock_provider3.name = "provider3"
        mock_provider3.normalize_data.return_value = {"BTC": 49000.0}

        aggregator = ProviderAggregator([mock_provider1, mock_provider2, mock_provider3])
        raw_data = {
            "provider1": {"data": {}},
            "provider2": {"data": {}},
            "provider3": {"data": {}}
        }
        
        result = aggregator.normalize_data(raw_data)

        # Average of 50000, 51000, 49000 = 50000
        assert result["BTC"]["results"] == 3
        assert result["BTC"]["avg_price"] == 50000.0
        assert result["BTC"]["sources"] == {
            "provider1": 50000.0,
            "provider2": 51000.0,
            "provider3": 49000.0
        }

    def test_normalize_data_different_symbols(self):
        """Test normalize_data when providers return different symbols."""
        mock_provider1 = Mock()
        mock_provider1.name = "provider1"
        mock_provider1.normalize_data.return_value = {"BTC": 50000.0, "ETH": 3000.0}

        mock_provider2 = Mock()
        mock_provider2.name = "provider2"
        mock_provider2.normalize_data.return_value = {"BTC": 51000.0}

        aggregator = ProviderAggregator([mock_provider1, mock_provider2])
        raw_data = {
            "provider1": {"data": {}},
            "provider2": {"data": {}}
        }
        
        result = aggregator.normalize_data(raw_data)

        assert result["BTC"]["results"] == 2
        assert result["BTC"]["avg_price"] == 50500.0
        assert result["ETH"]["results"] == 1
        assert result["ETH"]["avg_price"] == 3000.0

    def test_normalize_data_rounding(self):
        """Test that normalize_data properly rounds average prices."""
        mock_provider1 = Mock()
        mock_provider1.name = "provider1"
        mock_provider1.normalize_data.return_value = {"BTC": 50000.33}

        mock_provider2 = Mock()
        mock_provider2.name = "provider2"
        mock_provider2.normalize_data.return_value = {"BTC": 50000.67}

        aggregator = ProviderAggregator([mock_provider1, mock_provider2])
        raw_data = {
            "provider1": {"data": {}},
            "provider2": {"data": {}}
        }
        
        result = aggregator.normalize_data(raw_data)

        # Average should be rounded to 2 decimal places
        assert result["BTC"]["avg_price"] == 50000.5

    @patch('app.provider_aggregator.CoinGecko')
    @patch('app.provider_aggregator.Binance')
    @patch('app.provider_aggregator.Coinbase')
    def test_build_providers(self, mock_coinbase, mock_binance, mock_coin_gecko):
        """Test build_providers creates aggregator with all providers."""
        aggregator = build_providers()

        assert isinstance(aggregator, ProviderAggregator)
        assert len(aggregator.providers) == 3
        mock_coin_gecko.assert_called_once()
        mock_binance.assert_called_once()
        mock_coinbase.assert_called_once()
