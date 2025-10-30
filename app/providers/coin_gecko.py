from typing import Any
import requests
import httpx


class CoinGecko:
    name = "coin_gecko"
    url = "https://api.coingecko.com/api/v3/simple/price"

    coin_list = {"BTC": "bitcoin", "ETH": "ethereum", "SOL": "solana"}
    reverse_list = {"bitcoin": "BTC", "ethereum": "ETH", "solana": "SOL"}

    def fetch(self, symbols: list[str]) -> dict[str, Any]:
        """Used for sync calls"""
        query_param = self.convert_to_query_param(symbols=symbols)
        params = {"ids": query_param, "vs_currencies": "usd"}
        response = requests.get(self.url, params=params, timeout=60)

        data = response.json()

        return data
    
    async def afetch(self, symbols: list[str], client: httpx.AsyncClient) -> dict[str, Any]:
        """Used for async calls"""
        query_param = self.convert_to_query_param(symbols=symbols)
        params = {"ids": query_param, "vs_currencies": "usd"}
        response = await client.get(self.url, params=params, timeout=60)

        data = response.json()

        return data
    
    def normalize_data(self, raw_data: dict[str, Any]) -> dict[str, float]:
        return {self.reverse_list[k]: float(v["usd"]) for k,v in raw_data.items()}

    def convert_to_query_param(self, symbols: list[str]) -> str:
        return ",".join([self.coin_list[s] for s in symbols if s in self.coin_list])
