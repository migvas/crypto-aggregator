from typing import Any, Protocol
import httpx
import asyncio

from app.providers.coin_gecko import CoinGecko
from app.providers.binance import Binance
from app.providers.coinbase import Coinbase


class Provider(Protocol):
    name: str

    def fetch(self, symbols: list[str]) -> dict[str, Any]:  # type: ignore
        """Used for sync calls"""

    async def afetch(
        self, symbols: list[str], client: httpx.AsyncClient
    ) -> dict[str, Any]: # type: ignore
        """Used for async calls"""

    def normalize_data(self, raw_data: dict[str, Any]) -> dict[str, float]: # type: ignore
        """Normalize the returned data so we can present an unified format"""


class ProviderAggregator:
    def __init__(self, providers: list[Provider]):
        self.providers = providers

    def fetch_prices(self, symbols: list[str]) -> dict[str, Any]:
        price_results = {}
        for p in self.providers:
            price_results[p.name] = p.fetch(symbols=symbols)

        return price_results
    
    async def afetch_prices(self, symbols: list[str]) -> dict[str, Any]:
        async with httpx.AsyncClient(timeout=60) as client:
            async def call(p: Provider) -> tuple[str, dict[str, Any]]:
                try:
                    data = await p.afetch(symbols, client)
                    return p.name, {"ok": True, "data": data}
                except httpx.TimeoutException:
                    return p.name, {"ok": False, "error": "timeout"}
                except httpx.HTTPError as e:
                    code = e.response.status_code if e.response else "?"
                    return p.name, {"ok": False, "error": f"http {code}"}
                except Exception as e:
                    return p.name, {"ok": False, "error": str(e)}
        
            results = await asyncio.gather(*(call(p) for p in self.providers))
            return dict(results)
        
    def normalize_data(self, raw_data: dict[str, Any]) -> dict[str, dict[str, Any]]:
        merged_data = {}
        for p in self.providers:
            provider_data = p.normalize_data(raw_data[p.name]["data"])
            for coin, price in provider_data.items():
                if coin not in merged_data:
                    merged_data[coin] = {
                        "results": 0,
                        "avg_price": 0,
                        "sources": {}
                    }

                merged_data[coin]["results"] += 1
                merged_data[coin]["avg_price"] += price
                merged_data[coin]["sources"][p.name] = price

        
        for coin_details in merged_data.values():
            coin_details["avg_price"] = round(coin_details["avg_price"]/coin_details["results"], 2)

        return merged_data



def build_providers() -> ProviderAggregator:
    return ProviderAggregator([CoinGecko(), Binance(), Coinbase()])
