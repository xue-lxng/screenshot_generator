import asyncio
from typing import Dict, Any, Optional

import httpx

from core.caching.in_redis import cache

COINGECKO_FREE_URL = "https://api.coingecko.com/api/v3"
COINGECKO_PRO_URL  = "https://pro-api.coingecko.com/api/v3"



async def get_crypto_price(
    coin_symbol: str,
    vs_currency: str = "usd",
    api_key: Optional[str] = None,
    include_24h_change: bool = False,
    include_market_cap: bool = False,
    include_24h_vol: bool = False,
) -> dict:
    """
    Получить текущий курс крипто-пары по тикеру через CoinGecko API.

    Args:
        coin_symbol:        Тикер монеты (e.g. 'BTC', 'ETH', 'SOL')
        vs_currency:        Котируемая валюта (e.g. 'usd', 'eur', 'btc', 'eth')
        api_key:            API-ключ CoinGecko (Demo или Pro); None — бесплатный
        include_24h_change: Включить изменение цены за 24ч (%)
        include_market_cap: Включить рыночную капитализацию
        include_24h_vol:    Включить объём торгов за 24ч

    Returns:
        {
            "symbol": "BTC",
            "vs_currency": "USD",
            "price": 87500.12,
            "change_24h": 1.45,       # если include_24h_change=True
            "market_cap": 1_700_000_000_000,  # если include_market_cap=True
            "vol_24h": 32_000_000_000,         # если include_24h_vol=True
        }

    Raises:
        ValueError:   Монета не найдена
        httpx.HTTPStatusError: Ошибка HTTP
    """
    cache_key = f"{coin_symbol.lower()}_price_{vs_currency.lower()}"
    cached_rate = await cache.get(cache_key, compressed=True)
    if cached_rate:
        return cached_rate
    base_url = COINGECKO_PRO_URL if api_key else COINGECKO_FREE_URL

    headers = {}
    if api_key:
        # Demo key: x-cg-demo-api-key | Pro key: x-cg-pro-api-key
        headers["x-cg-demo-api-key"] = api_key

    params: dict = {
        "symbols": coin_symbol.lower(),
        "vs_currencies": vs_currency.lower(),
        "include_24hr_change": str(include_24h_change).lower(),
        "include_market_cap": str(include_market_cap).lower(),
        "include_24hr_vol": str(include_24h_vol).lower(),
    }

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{base_url}/simple/price",
            params=params,
            headers=headers,
        )
        response.raise_for_status()
        data: dict = response.json()

    if not data:
        raise ValueError(
            f"Монета с тикером '{coin_symbol.upper()}' не найдена на CoinGecko. "
            "Проверьте правильность символа."
        )

    # Ответ: {"bitcoin": {"usd": 87500.12, "usd_24h_change": 1.45, ...}}
    coin_data: dict = next(iter(data.values()))
    cur = vs_currency.lower()

    result = {
        "symbol": coin_symbol.upper(),
        "vs_currency": vs_currency.upper(),
        "price": coin_data.get(cur),
    }

    if include_24h_change:
        result["change_24h"] = coin_data.get(f"{cur}_24h_change")
    if include_market_cap:
        result["market_cap"] = coin_data.get(f"{cur}_market_cap")
    if include_24h_vol:
        result["vol_24h"] = coin_data.get(f"{cur}_24h_vol")

    if result:
        await cache.set(cache_key, result, compress=True, ttl=3600)

    return result

if __name__ == "__main__":
    print(asyncio.run(get_crypto_price("SOL", "usd")))  # Example usage
