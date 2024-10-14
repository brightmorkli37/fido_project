# schemas.py

from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Dict
from enum import Enum


class TransactionType(str, Enum):

    """Enum for transaction types."""
    credit = "credit"
    debit = "debit"

class TransactionCreate(BaseModel):

    """Schema for creating a new transaction."""
    user_id: str
    transaction_amount: float
    transaction_type: TransactionType


class TransactionUpdate(BaseModel):
    """Schema for updating a transaction."""

    transaction_amount: Optional[float]
    transaction_type: Optional[TransactionType]


class TransactionResponse(BaseModel):
    """Schema for returning transaction data."""

    id: str
    user_id: str
    full_name: str
    transaction_date: datetime
    transaction_amount: float
    transaction_type: TransactionType


class AnalyticsResponse(BaseModel):
    """Schema for the transaction analytics response."""

    user_id: str
    average_transaction_value: float
    highest_transaction_day: Optional[Dict[str, int]] = None  # {'year': int, 'month': int, 'day': int}
    total_debit: Optional[float] = None
    total_credit: Optional[float] = None

