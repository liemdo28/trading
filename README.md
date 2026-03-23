# trading

MVP backend cho **auto-trading trên Binance** theo yêu cầu “coding app trên binance”.

## Tính năng có sẵn

- API lấy lịch sử nến Binance Spot.
- API tạo tín hiệu EMA crossover (BUY/SELL/HOLD).
- API tạo trade plan với mặc định TP tối thiểu 10%.
- Tách `binance_client` và `strategy` để dễ tích hợp mobile/desktop app sau này.

## Cấu trúc

- `services/api/main.py`: FastAPI endpoints.
- `services/trading_engine/binance_client.py`: Binance REST client.
- `services/trading_engine/strategy.py`: logic tín hiệu và TP/SL plan.
- `tests/test_strategy.py`: unit test logic chiến lược.

## Chạy local

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn services.api.main:app --reload
```

## Endpoints

- `GET /health`
- `GET /binance/history?symbol=BTCUSDT&interval=1h&limit=200`
- `GET /binance/signal?symbol=BTCUSDT&interval=1h&tp_pct=0.10&sl_pct=0.03`

## Lưu ý bảo mật

- Không để API key trên app mobile/desktop.
- Chỉ backend mới giữ API secret.
- Nên dùng key quyền tối thiểu, bật IP whitelist.
