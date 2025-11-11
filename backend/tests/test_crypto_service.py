from decimal import Decimal
from sqlalchemy.orm import Session

from database import SessionLocal
from services.crypto.service import get_prices_kzt


def test_prices_fetch_and_format():
    db: Session = SessionLocal()
    prices = get_prices_kzt(db, ["BTC", "ETH", "USDT"], ttl_seconds=0)
    # Basic sanity checks
    assert "BTC" in prices
    assert "ETH" in prices
    assert "USDT" in prices
    assert isinstance(prices["BTC"], Decimal)
    assert prices["BTC"] > 0


