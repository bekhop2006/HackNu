from datetime import datetime
from sqlalchemy import Column, String, DateTime, Numeric
from database import Base


class CryptoPriceCache(Base):
    __tablename__ = "crypto_price_cache"

    symbol = Column(String(10), primary_key=True)
    price_kzt = Column(Numeric(18, 2), nullable=False)
    fetched_at = Column(DateTime, default=datetime.now, nullable=False)


