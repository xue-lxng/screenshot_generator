import datetime

from pydantic import BaseModel, field_validator, Field


class PhantomScreenshot(BaseModel):
    domain: str = Field(..., min_length=1, max_length=100)
    name: str = Field(..., min_length=1, max_length=50)
    amount: str = Field(..., min_length=1, max_length=20)
    multiplier: str = Field(..., min_length=1, max_length=20)

    token_name: str = Field(..., min_length=1, max_length=50)
    token_ticker: str = Field(..., min_length=1, max_length=20)
    token_amount: str = Field(..., min_length=1, max_length=30)
    token_amount_usd: str = Field(..., min_length=1, max_length=20)
    token_change: float
    token_logo: str | None = None

    solana_amount: float = Field(..., ge=0)
    solana_amount_usdt: float = Field(..., ge=0)
    solana_amount_change: float

    usdt_amount: float = Field(..., ge=0)
    usdt_amount_change: float

    current_time: str = Field(
        default_factory=lambda: datetime.datetime.utcnow().strftime("%H:%M")
    )

    @field_validator("current_time")
    @classmethod
    def validate_time_format(cls, v: str) -> str:
        try:
            datetime.datetime.strptime(v, "%H:%M")
        except ValueError:
            raise ValueError("current_time должен быть в формате HH:MM")
        return v

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

