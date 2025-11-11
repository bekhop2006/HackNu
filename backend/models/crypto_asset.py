from sqlalchemy import Column, String
from database import Base


class CryptoAsset(Base):
    __tablename__ = "crypto_assets"

    # Symbol as primary key, e.g., 'BTC', 'ETH', 'USDT'
    symbol = Column(String(10), primary_key=True, index=True)
    name = Column(String(100), nullable=False)


