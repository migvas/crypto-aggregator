from typing import Any
import asyncio
import requests
import httpx


class Binance:
    name = "binance"
    url = "https://api.binance.com/api/v3/ticker/price"

    def fetch(self, symbols: list[str]) -> dict[str, Any]:
        """Used for sync calls"""
        data_arr = []
        query_params = self.convert_to_query_param(symbols=symbols)
        for p in query_params:
            params = {"symbol": p}
            response = requests.get(self.url, params=params, timeout=60)
            data = response.json()
            data_arr.append(data)

        return {"result": data_arr}
    
    async def afetch(self, symbols: list[str], client: httpx.AsyncClient) -> dict[str, Any]:
        """Used for async calls"""
        query_param = self.convert_to_query_param(symbols=symbols)
    
        async def get_one_price(p: str):
            rr = await client.get(self.url, params={"symbol": p})
            rr.raise_for_status()
            return rr.json()

        data = await asyncio.gather(*[get_one_price(p) for p in query_param], return_exceptions=False)
        return {"result": data}
    
    def normalize_data(self, raw_data: dict[str, Any]) -> dict[str, float]:
        return {d["symbol"][:-4]: float(d["price"]) for d in raw_data["result"]}

    def convert_to_query_param(self, symbols: list[str]) -> list[str]:
        return [s + "USDC" for s in symbols]
    
