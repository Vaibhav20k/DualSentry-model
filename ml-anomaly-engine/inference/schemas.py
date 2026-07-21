from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)


class PredictionRequest(BaseModel):

    amount: float = Field(gt=0)

    payment_channel: Literal[
        "CARD",
        "UPI",
        "NET_BANKING",
        "WALLET",
    ]

    time_since_last_transaction: float = Field(ge=0)

    velocity_score: int = Field(ge=0)

    spending_deviation_score: float = Field(ge=0)

    is_first_transaction: int = Field(ge=0, le=1)

    hour: int = Field(ge=0, le=23)

    day_of_week: int = Field(ge=0, le=6)

    month: int = Field(ge=1, le=12)

    is_weekend: int = Field(ge=0, le=1)

    is_cross_bank_transfer: int = Field(ge=0, le=1)

    is_cross_currency_transfer: int = Field(ge=0, le=1)

    is_new_receiver: int = Field(ge=0, le=1)

    is_new_bank: int = Field(ge=0, le=1)

    is_new_payment_format: int = Field(ge=0, le=1)

class PredictionResponse(BaseModel):

    fraud_probability: float

    confidence: float

    prediction: bool

    threshold: float

    model_version: str