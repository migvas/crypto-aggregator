from typing import Any
import asyncio
import requests
import httpx

class Coinbase:
    name = "coinbase"
    url = "https://api.exchange.coinbase.com/products/symbol-USD/ticker"

    def fetch(self, symbols: list[str]) -> dict[str, Any]:
        """Used for sync calls"""
        data_obj = {}
        for s in symbols:
            query_url = self.url.replace("symbol", s)
            response = requests.get(query_url, timeout=60)
            data = response.json()
            data_obj[s] = data
        
        return data_obj

    async def afetch(self, symbols: list[str], client: httpx.AsyncClient) -> dict[str, Any]:
        """Used for async calls"""

        async def get_one_price(s: str) -> tuple[str, dict[str, Any]]:
            query_url = self.url.replace("symbol", s)
            rr = await client.get(query_url)
            rr.raise_for_status()
            return s, rr.json()

        data = await asyncio.gather(*[get_one_price(s) for s in symbols], return_exceptions=False)
        return dict(data)
    
    def normalize_data(self, raw_data: dict[str, Any]) -> dict[str, float]:
        return {k: float(v["price"]) for k,v in raw_data.items()}