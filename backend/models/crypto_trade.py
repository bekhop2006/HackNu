from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric
from database import Base


class CryptoTrade(Base):
    __tablename__ = "crypto_trades"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(10), ForeignKey("crypto_assets.symbol"), nullable=False, index=True)
    # 'buy' or 'sell'
    side = Column(String(4), nullable=False)

    # Quantity of crypto bought/sold and execution price in KZT
    quantity = Column(Numeric(28, 10), nullable=False)
    price_kzt = Column(Numeric(18, 2), nullable=False)
    notional_kzt = Column(Numeric(18, 2), nullable=False)

    created_at = Column(DateTime, default=datetime.now)


