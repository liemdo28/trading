from services.trading_engine.strategy import build_trade_plan, crossover_signal


def test_build_trade_plan_buy_target_10pct() -> None:
    plan = build_trade_plan(last_price=100.0, signal="BUY", min_take_profit_pct=0.10, stop_loss_pct=0.03)
    assert plan.take_profit == 110.0
    assert plan.stop_loss == 97.0
    assert plan.risk_reward > 3


def test_crossover_signal_hold_when_not_enough_data() -> None:
    signal = crossover_signal([1.0, 1.1, 1.2], fast_period=9, slow_period=21)
    assert signal == "HOLD"
