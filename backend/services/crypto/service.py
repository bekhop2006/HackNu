from datetime import datetime, timedelta
from decimal import Decimal, ROUND_DOWN
from typing import Dict, List, Tuple

import requests
from sqlalchemy.orm import Session

from database import get_db
from models import CryptoAccount, CryptoAsset, CryptoPriceCache, CryptoTrade, Account
from services.transaction.service import create_deposit, create_withdrawal
from services.transaction.schemas import TransactionDeposit, TransactionWithdrawal

SUPPORTED = ("BTC", "ETH", "USDT")
COINGECKO_IDS = {"BTC": "bitcoin", "ETH": "ethereum", "USDT": "tether"}


def ensure_assets_seeded(db: Session) -> None:
    for sym, name in [("BTC", "Bitcoin"), ("ETH", "Ethereum"), ("USDT", "Tether")]:
        if not db.query(CryptoAsset).filter(CryptoAsset.symbol == sym).first():
            db.add(CryptoAsset(symbol=sym, name=name))
    db.commit()


def _fetch_price_from_coingecko(symbols: List[str]) -> Dict[str, Decimal]:
    ids = ",".join(COINGECKO_IDS[s] for s in symbols)
    url = f"https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=kzt"
    res = requests.get(url, timeout=10)
    res.raise_for_status()
    data = res.json()
    out: Dict[str, Decimal] = {}
    for s in symbols:
        price = data.get(COINGECKO_IDS[s], {}).get("kzt")
        if price is None:
            raise ValueError(f"Price for {s} not available")
        out[s] = Decimal(str(price)).quantize(Decimal("0.01"))
    return out


def get_prices_kzt(db: Session, symbols: List[str], ttl_seconds: int = 30) -> Dict[str, Decimal]:
    now = datetime.utcnow()
    fresh: Dict[str, Decimal] = {}
    missing: List[str] = []

    for s in symbols:
        rec = db.query(CryptoPriceCache).filter(CryptoPriceCache.symbol == s).first()
        if rec and (now - rec.fetched_at) <= timedelta(seconds=ttl_seconds):
            fresh[s] = Decimal(rec.price_kzt).quantize(Decimal("0.01"))
        else:
            missing.append(s)

    if missing:
        fetched = _fetch_price_from_coingecko(missing)
        for s, price in fetched.items():
            rec = db.query(CryptoPriceCache).filter(CryptoPriceCache.symbol == s).first()
            if rec:
                rec.price_kzt = price
                rec.fetched_at = now
            else:
                db.add(CryptoPriceCache(symbol=s, price_kzt=price, fetched_at=now))
        db.commit()
        fresh.update(fetched)

    return fresh


def get_user_balances(db: Session, user_id: int) -> Tuple[List[Dict], Decimal]:
    ensure_assets_seeded(db)
    accounts = db.query(CryptoAccount).filter(CryptoAccount.user_id == user_id).all()
    by_symbol = {a.symbol: a for a in accounts}

    # Guarantee rows for supported symbols
    for sym in SUPPORTED:
        if sym not in by_symbol:
            acct = CryptoAccount(user_id=user_id, symbol=sym, balance=Decimal("0"))
            db.add(acct)
            by_symbol[sym] = acct
    db.commit()

    prices = get_prices_kzt(db, list(SUPPORTED))
    items: List[Dict] = []
    total = Decimal("0.00")

    for sym in SUPPORTED:
        qty = Decimal(by_symbol[sym].balance or 0).quantize(Decimal("0.0000000001"))
        price = prices[sym]
        value = (qty * price).quantize(Decimal("0.01"))
        items.append(
            {
                "symbol": sym,
                "quantity": qty,
                "price_kzt": price,
                "value_kzt": value,
            }
        )
        total += value

    return items, total.quantize(Decimal("0.01"))


def _get_kzt_wallet(db: Session, user_id: int, kzt_account_id: int) -> Account:
    wallet = db.query(Account).filter(Account.id == kzt_account_id).first()
    if not wallet or wallet.user_id != user_id or wallet.currency != "KZT" or wallet.status != "active":
        raise ValueError("Invalid KZT wallet account")
    return wallet


def market_buy(db: Session, user_id: int, symbol: str, kzt_amount: Decimal, kzt_account_id: int) -> Dict:
    if symbol not in SUPPORTED:
        raise ValueError("Unsupported symbol")
    if kzt_amount <= 0:
        raise ValueError("Amount must be positive")

    ensure_assets_seeded(db)

    # Validate KZT wallet
    _get_kzt_wallet(db, user_id, kzt_account_id)

    price = get_prices_kzt(db, [symbol])[symbol]
    qty = (kzt_amount / price).quantize(Decimal("0.0000000001"), rounding=ROUND_DOWN)

    # Withdraw KZT from wallet
    withdrawal = TransactionWithdrawal(
        account_id=kzt_account_id,
        amount=kzt_amount,
        currency="KZT",
        description=f"BUY {symbol} (market)",
    )
    create_withdrawal(withdrawal, user_id, db)

    # Credit crypto balance
    acct = db.query(CryptoAccount).filter(CryptoAccount.user_id == user_id, CryptoAccount.symbol == symbol).first()
    if not acct:
        acct = CryptoAccount(user_id=user_id, symbol=symbol, balance=Decimal("0"))
        db.add(acct)
        db.commit()
        db.refresh(acct)
    acct.balance = Decimal(acct.balance or 0) + qty
    db.add(
        CryptoTrade(
            user_id=user_id,
            symbol=symbol,
            side="buy",
            quantity=qty,
            price_kzt=price,
            notional_kzt=kzt_amount,
        )
    )
    db.commit()

    return {"symbol": symbol, "quantity": qty, "price_kzt": price, "notional_kzt": kzt_amount}


def market_sell(db: Session, user_id: int, symbol: str, quantity: Decimal, kzt_account_id: int) -> Dict:
    if symbol not in SUPPORTED:
        raise ValueError("Unsupported symbol")
    if quantity <= 0:
        raise ValueError("Quantity must be positive")

    ensure_assets_seeded(db)

    # Validate KZT wallet
    _get_kzt_wallet(db, user_id, kzt_account_id)

    acct = db.query(CryptoAccount).filter(CryptoAccount.user_id == user_id, CryptoAccount.symbol == symbol).first()
    if not acct or Decimal(acct.balance or 0) < quantity:
        raise ValueError("Insufficient crypto balance")

    price = get_prices_kzt(db, [symbol])[symbol]
    proceeds = (quantity * price).quantize(Decimal("0.01"))

    # Debit crypto balance
    acct.balance = Decimal(acct.balance) - quantity

    # Deposit KZT to wallet
    deposit = TransactionDeposit(
        account_id=kzt_account_id,
        amount=proceeds,
        currency="KZT",
        description=f"SELL {symbol} (market)",
    )
    create_deposit(deposit, user_id, db)

    db.add(
        CryptoTrade(
            user_id=user_id,
            symbol=symbol,
            side="sell",
            quantity=quantity,
            price_kzt=price,
            notional_kzt=proceeds,
        )
    )
    db.commit()

    return {"symbol": symbol, "quantity": quantity, "price_kzt": price, "notional_kzt": proceeds}


