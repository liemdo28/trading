"""Simple strategy helpers for Binance auto-trading MVP."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Literal

Signal = Literal["BUY", "SELL", "HOLD"]


@dataclass
class TradePlan:
    signal: Signal
    entry_price: float
    stop_loss: float
    take_profit: float
    risk_reward: float


def ema(values: Iterable[float], period: int) -> List[float]:
    values = list(values)
    if not values:
        return []

    multiplier = 2 / (period + 1)
    result: List[float] = [values[0]]
    for value in values[1:]:
        next_ema = (value - result[-1]) * multiplier + result[-1]
        result.append(next_ema)
    return result


def crossover_signal(closes: List[float], fast_period: int = 9, slow_period: int = 21) -> Signal:
    if len(closes) < max(fast_period, slow_period) + 2:
        return "HOLD"

    fast = ema(closes, fast_period)
    slow = ema(closes, slow_period)

    prev_fast, curr_fast = fast[-2], fast[-1]
    prev_slow, curr_slow = slow[-2], slow[-1]

    if prev_fast <= prev_slow and curr_fast > curr_slow:
        return "BUY"
    if prev_fast >= prev_slow and curr_fast < curr_slow:
        return "SELL"
    return "HOLD"


def build_trade_plan(
    last_price: float,
    signal: Signal,
    min_take_profit_pct: float = 0.10,
    stop_loss_pct: float = 0.03,
) -> TradePlan:
    """Build a simple trade plan using minimum 10% TP target by default."""

    if signal == "BUY":
        entry = last_price
        tp = entry * (1 + min_take_profit_pct)
        sl = entry * (1 - stop_loss_pct)
    elif signal == "SELL":
        entry = last_price
        tp = entry * (1 - min_take_profit_pct)
        sl = entry * (1 + stop_loss_pct)
    else:
        entry = last_price
        tp = last_price
        sl = last_price

    risk = abs(entry - sl)
    reward = abs(tp - entry)
    rr = reward / risk if risk else 0.0

    return TradePlan(
        signal=signal,
        entry_price=round(entry, 8),
        stop_loss=round(sl, 8),
        take_profit=round(tp, 8),
        risk_reward=round(rr, 4),
    )
