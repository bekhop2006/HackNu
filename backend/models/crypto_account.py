from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Numeric, UniqueConstraint
from sqlalchemy.orm import relationship
from database import Base


class CryptoAccount(Base):
    __tablename__ = "crypto_accounts"
    __table_args__ = (
        UniqueConstraint("user_id", "symbol", name="uq_crypto_account_user_symbol"),
    )

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    symbol = Column(String(10), ForeignKey("crypto_assets.symbol"), nullable=False, index=True)
    # High precision for balances
    balance = Column(Numeric(28, 10), default=0)

    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)

    # Relationships
    user = relationship("User")


