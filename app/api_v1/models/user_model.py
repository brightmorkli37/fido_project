from bson import ObjectId
from pydantic import GetCoreSchemaHandler, BaseModel, Field, EmailStr
from pydantic_core import core_schema
from datetime import datetime, timezone
from typing import Optional
import pytz


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

class UserModel(BaseModel):
    """Pydantic model for user representation in MongoDB."""
    
    id: Optional[PyObjectId] = Field(
        default=None,
        validation_alias='id',          # Accept 'id' during validation
        serialization_alias='_id'       # Use '_id' during serialization
    )
    full_name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    model_config = {
        "arbitrary_types_allowed": True,
        "json_encoders": {ObjectId: str},
    }

