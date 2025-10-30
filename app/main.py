from fastapi import FastAPI, Query, HTTPException
from app.provider_aggregator import build_providers
from app.models import PriceResponse, SymbolView

app = FastAPI(title="Crypto Price Aggregator")
pagg = build_providers()


@app.get("/prices", response_model=PriceResponse)
def get_prices(
    q: str = Query(..., description="Comma-separated symbols, e.g. BTC,ETH")
):
    symbols = [s.strip().upper() for s in q.split(",") if s.strip()]
    if not symbols:
        raise HTTPException(400, "No symbols provided")

    provider_results = pagg.fetch_prices(symbols)

    merged = pagg.normalize_data(provider_results)

    symbols = {k: SymbolView(**v) for k, v in merged.items()}
    if not symbols:
        # no provider returned anything useful
        raise HTTPException(503, "No data available from upstream providers")

    return {"symbols": symbols}


@app.get("/async_prices", response_model=PriceResponse)
async def async_get_prices(
    q: str = Query(..., description="Comma-separated symbols, e.g. BTC,ETH")
):
    symbols = [s.strip().upper() for s in q.split(",") if s.strip()]
    if not symbols:
        raise HTTPException(400, "No symbols provided")

    provider_results = await pagg.afetch_prices(symbols)

    merged = pagg.normalize_data(provider_results)
    # merged: dict[str, Any] = {"note": "Normalization pending in next step"}
    symbols = {k: SymbolView(**v) for k, v in merged.items()}
    if not symbols:
        # no provider returned anything useful
        raise HTTPException(503, "No data available from upstream providers")

    return {"symbols": symbols}
