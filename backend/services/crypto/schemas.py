from decimal import Decimal
from pydantic import BaseModel, Field, condecimal, constr
from typing import List


SupportedSymbol = constr(to_upper=True, strip_whitespace=True, pattern="^(BTC|ETH|USDT)$")


class PriceResponse(BaseModel):
    symbol: SupportedSymbol
    price_kzt: condecimal(max_digits=18, decimal_places=2)


class BalancesItem(BaseModel):
    symbol: SupportedSymbol
    quantity: condecimal(max_digits=28, decimal_places=10) = Decimal("0")
    price_kzt: condecimal(max_digits=18, decimal_places=2)
    value_kzt: condecimal(max_digits=18, decimal_places=2)


class BalancesResponse(BaseModel):
    items: List[BalancesItem]
    total_value_kzt: condecimal(max_digits=18, decimal_places=2)


class MarketBuyRequest(BaseModel):
    symbol: SupportedSymbol = Field(description="BTC, ETH or USDT")
    kzt_amount: condecimal(gt=0, max_digits=18, decimal_places=2)
    kzt_account_id: int = Field(description="Destination wallet account (KZT) to debit during buy")


class MarketSellRequest(BaseModel):
    symbol: SupportedSymbol
    quantity: condecimal(gt=0, max_digits=28, decimal_places=10)
    kzt_account_id: int = Field(description="Destination wallet account (KZT) to credit during sell")


