from pydantic import BaseModel, Field
from typing import Dict

class SymbolView(BaseModel):
    avg_price: float = Field(..., description="Average price of sources")
    results: int = Field(..., description="Number of sources")
    sources: Dict[str, float]  # {provider_name: price}

class PriceResponse(BaseModel):
    symbols: Dict[str, SymbolView]  # {symbol: SymbolView}