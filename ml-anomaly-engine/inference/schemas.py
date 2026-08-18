from typing import Literal

from pydantic import (
    BaseModel,
    Field,
)
from pydantic import BaseModel
from typing import List, Dict, Any


class PredictionRequest(BaseModel):

    amount: float = Field(gt=0)

    payment_channel: Literal[
        "CARD",
        "UPI",
        "NET_BANKING",
        "WALLET",
    ]

    time_since_last_transaction: float = Field(ge=0)

    velocity_score: float = Field(ge=0)

    spending_deviation_score: float

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
    reason_codes: list[str]    


class ModelInfoResponse(BaseModel):
    model_id: str
    version: str
    algorithm: str
    status: str

    description: str

    path: str

    artifacts: Dict[str, str]

    dataset_version: str
    feature_schema_version: str
    training_run_id: str

    created_at: str
    updated_at: str

    metrics: Dict[str, Any]
    training_stats: Dict[str, Any]


class ModelListResponse(BaseModel):
    active_model: str
    models: List[ModelInfoResponse]


class ActivateModelRequest(BaseModel):
    model_id: str


class RegisterModelRequest(BaseModel):
    model_id: str
    version: str
    algorithm: str
    description: str

    path: str

    artifacts: Dict[str, str]

    dataset_version: str
    feature_schema_version: str
    training_run_id: str

    metrics: Dict[str, Any]
    training_stats: Dict[str, Any]


class OperationResponse(BaseModel):
    success: bool
    message: str

class MonitoringResponse(BaseModel):

    total_predictions: int

    fraud_predictions: int

    fraud_rate: float

    average_confidence: float

    average_probability: float