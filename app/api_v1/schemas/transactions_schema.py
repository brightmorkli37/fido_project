from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class TransactionType(str, Enum):
    credit = "credit"
    debit = "debit"


class TransactionCreate(BaseModel):
    transaction_date: datetime
    transaction_amount: float
    transaction_type: TransactionType
