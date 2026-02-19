import datetime
import random

from pydantic import BaseModel, field_validator, Field


class PhantomScreenshot(BaseModel):
    domain: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=50)
    amount: str = Field(..., min_length=1, max_length=7)
    multiplier: str = Field(..., min_length=1, max_length=20)

    usdt_amount: float
    token_name: str = Field(..., min_length=1, max_length=50)
    token_ticker: str = Field(..., min_length=1, max_length=20)
    token_amount: float
    usd_price_per_token: float
    token_logo: str | None = None

    @field_validator("token_logo")
    @classmethod
    def validate_logo(cls, v: str | None) -> str | None:
        if v and not v.startswith("data:image/"):
            raise ValueError("token_logo должен быть data URI (data:image/...)")
        return v

    @field_validator("multiplier")
    @classmethod
    def validate_multiplier(cls, v: str) -> str:
        try:
            if float(v) <= 0:
                raise ValueError
        except ValueError:
            raise ValueError("multiplier должен быть положительным числом")
        return v

