from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from database import get_db
from .schemas import (
    MarketBuyRequest,
    MarketSellRequest,
    BalancesResponse,
    BalancesItem,
    PriceResponse,
)
from .service import get_user_balances, get_prices_kzt, market_buy, market_sell, SUPPORTED

router = APIRouter(prefix="/api/crypto", tags=["Crypto"])


@router.get("/prices", response_model=list[PriceResponse])
def get_prices(db: Session = Depends(get_db)):
    prices = get_prices_kzt(db, list(SUPPORTED))
    return [{"symbol": s, "price_kzt": p} for s, p in prices.items()]


@router.get("/portfolio/balances", response_model=BalancesResponse)
def get_balances(user_id: int = Query(..., description="Authenticated user id"),
                 db: Session = Depends(get_db)):
    try:
        items, total = get_user_balances(db, user_id)
        return BalancesResponse(
            items=[BalancesItem(**it) for it in items],
            total_value_kzt=total,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/market/buy")
def post_market_buy(payload: MarketBuyRequest,
                    user_id: int = Query(..., description="Authenticated user id"),
                    db: Session = Depends(get_db)):
    try:
        res = market_buy(
            db,
            user_id=user_id,
            symbol=payload.symbol,
            kzt_amount=Decimal(str(payload.kzt_amount)),
            kzt_account_id=payload.kzt_account_id,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/orders/market/sell")
def post_market_sell(payload: MarketSellRequest,
                     user_id: int = Query(..., description="Authenticated user id"),
                     db: Session = Depends(get_db)):
    try:
        res = market_sell(
            db,
            user_id=user_id,
            symbol=payload.symbol,
            quantity=Decimal(str(payload.quantity)),
            kzt_account_id=payload.kzt_account_id,
        )
        return res
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


