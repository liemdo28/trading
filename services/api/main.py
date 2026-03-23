from __future__ import annotations

import os
from typing import List

from fastapi import FastAPI, HTTPException, Query
from pydantic import BaseModel

from services.trading_engine.binance_client import BinanceClient
from services.trading_engine.strategy import build_trade_plan, crossover_signal

app = FastAPI(title="Trading API (Binance MVP)", version="0.1.0")


class Candle(BaseModel):
    open_time: int
    open: float
    high: float
    low: float
    close: float
    volume: float
    close_time: int


class SignalResponse(BaseModel):
    symbol: str
    interval: str
    signal: str
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float


def get_client() -> BinanceClient:
    return BinanceClient(
        api_key=os.getenv("BINANCE_API_KEY"),
        api_secret=os.getenv("BINANCE_API_SECRET"),
        base_url=os.getenv("BINANCE_BASE_URL", "https://api.binance.com"),
    )


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.get("/binance/history", response_model=List[Candle])
def binance_history(
    symbol: str = Query(default="BTCUSDT"),
    interval: str = Query(default="1h"),
    limit: int = Query(default=200, ge=10, le=1000),
) -> List[Candle]:
    client = get_client()
    try:
        data = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    except Exception as exc:  # upstream API/network
        raise HTTPException(status_code=502, detail=f"Binance error: {exc}") from exc

    return [
        Candle(
            open_time=int(row[0]),
            open=float(row[1]),
            high=float(row[2]),
            low=float(row[3]),
            close=float(row[4]),
            volume=float(row[5]),
            close_time=int(row[6]),
        )
        for row in data
    ]


@app.get("/binance/signal", response_model=SignalResponse)
def binance_signal(
    symbol: str = Query(default="BTCUSDT"),
    interval: str = Query(default="1h"),
    limit: int = Query(default=200, ge=30, le=1000),
    tp_pct: float = Query(default=0.10, ge=0.01, le=1.0),
    sl_pct: float = Query(default=0.03, ge=0.005, le=0.5),
) -> SignalResponse:
    client = get_client()
    try:
        candles = client.get_klines(symbol=symbol, interval=interval, limit=limit)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Binance error: {exc}") from exc

    closes = [float(c[4]) for c in candles]
    signal = crossover_signal(closes)
    plan = build_trade_plan(
        last_price=closes[-1],
        signal=signal,
        min_take_profit_pct=tp_pct,
        stop_loss_pct=sl_pct,
    )

    return SignalResponse(
        symbol=symbol.upper(),
        interval=interval,
        signal=plan.signal,
        entry_price=plan.entry_price,
        stop_loss=plan.stop_loss,
        take_profit=plan.take_profit,
        risk_reward=plan.risk_reward,
    )
