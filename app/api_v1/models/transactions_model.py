
from bson import ObjectId
from datetime import datetime, timezone
from enum import Enum
from pydantic_core import core_schema
from pydantic import BaseModel, GetCoreSchemaHandler, Field
from typing import Optional


class PyObjectId(ObjectId):
    """Custom ObjectId type for Pydantic models."""
    
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        """Validate if the value is a valid ObjectId."""
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid ObjectId")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_core_schema__(
        cls, source_type: any, handler: GetCoreSchemaHandler
    ) -> core_schema.CoreSchema:
        """Define core schema for Pydantic."""
        return core_schema.json_or_python_schema(
            json_schema=core_schema.str_schema(),
            python_schema=core_schema.union_schema([
                core_schema.is_instance_schema(ObjectId),
                core_schema.chain_schema([
                    core_schema.str_schema(),
                    core_schema.no_info_plain_validator_function(cls.validate),
                ]),
            ]),
            serialization=core_schema.plain_serializer_function_ser_schema(str),
        )

class TransactionType(str, Enum):
    """Enum for transaction types."""
    credit = "credit"
    debit = "debit"
    

class TransactionModel(BaseModel):
    """Pydantic model for transaction representation in MongoDB."""

    id: Optional[PyObjectId] = Field(default=None, alias="_id")
    user_id: PyObjectId = Field(...)
    full_name: str = Field(...)
    transaction_date: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    transaction_amount: float = Field(...)
    transaction_type: TransactionType = Field(...)

    model_config = {
        "populate_by_name": True,
        "arbitrary_types_allowed": True,
    }
