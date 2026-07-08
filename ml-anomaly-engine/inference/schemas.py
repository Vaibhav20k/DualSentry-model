from pydantic import BaseModel


class PredictionRequest(BaseModel):

    amount: float

    transaction_type: str

    merchant_category: str

    location: str

    device_used: str

    payment_channel: str

    time_since_last_transaction: float

    spending_deviation_score: float

    velocity_score: int

    geo_anomaly_score: float

    hour: int

    day_of_week: int

    month: int

    is_weekend: int

    is_first_transaction: int


class PredictionResponse(BaseModel):

    fraud_probability: float

    prediction: bool

    threshold: float

    model_version: str