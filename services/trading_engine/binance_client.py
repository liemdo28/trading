"""Binance Spot client (public + minimal signed helpers).

This module intentionally keeps dependencies minimal and can be shared by
API service and worker processes.
"""

from __future__ import annotations

import hashlib
import hmac
import time
from typing import Any, Dict, List, Optional
from urllib.parse import urlencode

import httpx


class BinanceClient:
    """Simple Binance REST API client."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        base_url: str = "https://api.binance.com",
        timeout: float = 15.0,
    ) -> None:
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def _request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        signed: bool = False,
    ) -> Any:
        params = params or {}
        headers: Dict[str, str] = {}

        if signed:
            if not self.api_key or not self.api_secret:
                raise ValueError("Signed endpoint requires API key and secret")
            params["timestamp"] = int(time.time() * 1000)
            query = urlencode(params)
            signature = hmac.new(
                self.api_secret.encode("utf-8"),
                query.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            params["signature"] = signature
            headers["X-MBX-APIKEY"] = self.api_key
        elif self.api_key:
            headers["X-MBX-APIKEY"] = self.api_key

        with httpx.Client(timeout=self.timeout) as client:
            response = client.request(
                method=method,
                url=f"{self.base_url}{path}",
                params=params,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()

    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[List[Any]]:
        """Fetch OHLCV candles.

        Reference: GET /api/v3/klines
        """
        return self._request(
            "GET",
            "/api/v3/klines",
            params={"symbol": symbol.upper(), "interval": interval, "limit": limit},
        )

    def get_ticker_price(self, symbol: str) -> Dict[str, str]:
        """Fetch latest price for symbol."""
        return self._request(
            "GET",
            "/api/v3/ticker/price",
            params={"symbol": symbol.upper()},
        )

    def get_account(self) -> Dict[str, Any]:
        """Fetch account balances (signed endpoint)."""
        return self._request("GET", "/api/v3/account", signed=True)

    def create_test_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
    ) -> Dict[str, Any]:
        """Create Binance test order to validate order params safely."""
        params: Dict[str, Any] = {
            "symbol": symbol.upper(),
            "side": side.upper(),
            "type": order_type.upper(),
            "quantity": quantity,
        }
        if price is not None:
            params["price"] = price
            params["timeInForce"] = "GTC"

        return self._request("POST", "/api/v3/order/test", params=params, signed=True)
