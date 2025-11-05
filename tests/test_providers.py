"""Unit tests for provider classes with mocked external API calls."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
import httpx
from app.providers.coin_gecko import CoinGecko
from app.providers.binance import Binance
from app.providers.coinbase import Coinbase


class TestCoinGecko:
    """Test CoinGecko provider with mocked requests."""

    def test_convert_to_query_param(self):
        """Test converting symbols to CoinGecko coin IDs."""
        provider = CoinGecko()
        result = provider.convert_to_query_param(["BTC", "ETH"])
        assert result == "bitcoin,ethereum"

    def test_convert_to_query_param_with_unsupported_symbol(self):
        """Test converting symbols when some are not supported."""
        provider = CoinGecko()
        result = provider.convert_to_query_param(["BTC", "UNKNOWN"])
        assert result == "bitcoin"

    @patch('app.providers.coin_gecko.requests.get')
    def test_fetch_success(self, mock_get):
        """Test successful sync fetch of prices."""
        mock_response = Mock()
        mock_response.json.return_value = {
            "bitcoin": {"usd": 50000.0},
            "ethereum": {"usd": 3000.0}
        }
        mock_get.return_value = mock_response

        provider = CoinGecko()
        result = provider.fetch(["BTC", "ETH"])

        assert result == {
            "bitcoin": {"usd": 50000.0},
            "ethereum": {"usd": 3000.0}
        }
        mock_get.assert_called_once()
        call_args = mock_get.call_args
        assert call_args[1]['params']['ids'] == "bitcoin,ethereum"
        assert call_args[1]['params']['vs_currencies'] == "usd"

    @pytest.mark.asyncio
    async def test_afetch_success(self):
        """Test successful async fetch of prices."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_response = Mock()
        mock_response.json.return_value = {
            "bitcoin": {"usd": 50000.0},
            "ethereum": {"usd": 3000.0}
        }
        mock_client.get.return_value = mock_response

        provider = CoinGecko()
        result = await provider.afetch(["BTC", "ETH"], mock_client)

        assert result == {
            "bitcoin": {"usd": 50000.0},
            "ethereum": {"usd": 3000.0}
        }
        mock_client.get.assert_called_once()

    def test_normalize_data(self):
        """Test normalizing CoinGecko response data."""
        provider = CoinGecko()
        raw_data = {
            "bitcoin": {"usd": 50000.0},
            "ethereum": {"usd": 3000.0}
        }
        result = provider.normalize_data(raw_data)

        assert result == {
            "BTC": 50000.0,
            "ETH": 3000.0
        }


class TestBinance:
    """Test Binance provider with mocked requests."""

    def test_convert_to_query_param(self):
        """Test converting symbols to Binance trading pairs."""
        provider = Binance()
        result = provider.convert_to_query_param(["BTC", "ETH"])
        assert result == ["BTCUSDC", "ETHUSDC"]

    @patch('app.providers.binance.requests.get')
    def test_fetch_success(self, mock_get):
        """Test successful sync fetch of prices."""
        mock_responses = [
            Mock(json=lambda: {"symbol": "BTCUSDC", "price": "50000.0"}),
            Mock(json=lambda: {"symbol": "ETHUSDC", "price": "3000.0"})
        ]
        mock_get.side_effect = mock_responses

        provider = Binance()
        result = provider.fetch(["BTC", "ETH"])

        assert result == {
            "result": [
                {"symbol": "BTCUSDC", "price": "50000.0"},
                {"symbol": "ETHUSDC", "price": "3000.0"}
            ]
        }
        assert mock_get.call_count == 2

    @pytest.mark.asyncio
    async def test_afetch_success(self):
        """Test successful async fetch of prices."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        
        async def mock_get_side_effect(url, params):
            mock_response = Mock()
            if params["symbol"] == "BTCUSDC":
                mock_response.json.return_value = {"symbol": "BTCUSDC", "price": "50000.0"}
            else:
                mock_response.json.return_value = {"symbol": "ETHUSDC", "price": "3000.0"}
            mock_response.raise_for_status = Mock()
            return mock_response
        
        mock_client.get.side_effect = mock_get_side_effect

        provider = Binance()
        result = await provider.afetch(["BTC", "ETH"], mock_client)

        assert result == {
            "result": [
                {"symbol": "BTCUSDC", "price": "50000.0"},
                {"symbol": "ETHUSDC", "price": "3000.0"}
            ]
        }
        assert mock_client.get.call_count == 2

    def test_normalize_data(self):
        """Test normalizing Binance response data."""
        provider = Binance()
        raw_data = {
            "result": [
                {"symbol": "BTCUSDC", "price": "50000.0"},
                {"symbol": "ETHUSDC", "price": "3000.0"}
            ]
        }
        result = provider.normalize_data(raw_data)

        assert result == {
            "BTC": 50000.0,
            "ETH": 3000.0
        }


class TestCoinbase:
    """Test Coinbase provider with mocked requests."""

    @patch('app.providers.coinbase.requests.get')
    def test_fetch_success(self, mock_get):
        """Test successful sync fetch of prices."""
        mock_responses = [
            Mock(json=lambda: {"price": "50000.0"}),
            Mock(json=lambda: {"price": "3000.0"})
        ]
        mock_get.side_effect = mock_responses

        provider = Coinbase()
        result = provider.fetch(["BTC", "ETH"])

        assert result == {
            "BTC": {"price": "50000.0"},
            "ETH": {"price": "3000.0"}
        }
        assert mock_get.call_count == 2

    @pytest.mark.asyncio
    async def test_afetch_success(self):
        """Test successful async fetch of prices."""
        mock_client = AsyncMock(spec=httpx.AsyncClient)
        
        async def mock_get_side_effect(url):
            mock_response = Mock()
            if "BTC" in url:
                mock_response.json.return_value = {"price": "50000.0"}
            else:
                mock_response.json.return_value = {"price": "3000.0"}
            mock_response.raise_for_status = Mock()
            return mock_response
        
        mock_client.get.side_effect = mock_get_side_effect

        provider = Coinbase()
        result = await provider.afetch(["BTC", "ETH"], mock_client)

        assert result == {
            "BTC": {"price": "50000.0"},
            "ETH": {"price": "3000.0"}
        }
        assert mock_client.get.call_count == 2

    def test_normalize_data(self):
        """Test normalizing Coinbase response data."""
        provider = Coinbase()
        raw_data = {
            "BTC": {"price": "50000.0"},
            "ETH": {"price": "3000.0"}
        }
        result = provider.normalize_data(raw_data)

        assert result == {
            "BTC": 50000.0,
            "ETH": 3000.0
        }
