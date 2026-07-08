from datetime import datetime
from typing import Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_validator,
)


TransactionType = Literal[
    "CASH_IN",
    "CASH_OUT",
    "DEBIT",
    "PAYMENT",
    "TRANSFER",
]


class TransactionInput(BaseModel):
    amount: float = Field(..., gt=0)
    oldbalanceOrg: float = Field(..., ge=0)
    newbalanceOrig: float = Field(..., ge=0)
    oldbalanceDest: float = Field(..., ge=0)
    newbalanceDest: float = Field(..., ge=0)
    type: TransactionType

    @field_validator("type", mode="before")
    @classmethod
    def normalize_transaction_type(cls, value):
        if isinstance(value, str):
            return value.upper()

        return value


class PredictionResponse(BaseModel):
    prediction_id: int
    prediction: str
    risk_level: str
    fraud_probability: float
    threshold_used: float
    model_version: str


class PredictionRecord(BaseModel):
    id: int
    user_id: int

    transaction_type: str
    amount: float
    oldbalanceOrg: float
    newbalanceOrig: float
    oldbalanceDest: float
    newbalanceDest: float

    prediction: str
    risk_level: str
    fraud_probability: float
    threshold_used: float
    model_version: str

    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=6)


class UserResponse(BaseModel):
    id: int
    email: EmailStr
    created_at: datetime

    model_config = ConfigDict(
        from_attributes=True,
    )


class Token(BaseModel):
    access_token: str
    token_type: str


class ModelInfoResponse(BaseModel):
    model_version: str
    sklearn_version: str
    threshold_used: float
    model_type: str
    features: list[str]