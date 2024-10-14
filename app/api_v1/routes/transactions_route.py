# routes.py

from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from app.api_v1.schemas import (
    TransactionCreate,
    TransactionUpdate,
    TransactionResponse,
)
from app.api_v1.models import TransactionModel
from db.database import get_database
from cryptography.fernet import Fernet
from app.api_v1.utils import generate_key
from app.api_v1.utils.encrypt_decrypt import safe_decrypt

router = APIRouter()

ENCRYPTION_KEY = generate_key.get_encryption_key()
fernet = Fernet(ENCRYPTION_KEY.encode())

# Create a transaction
@router.post("/transactions/", response_model=TransactionResponse)
async def create_transaction(transaction: TransactionCreate, db=Depends(get_database)):
    try:
        # Convert user_id to ObjectId
        try:
            user_oid = ObjectId(transaction.user_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        # Find the user to get full_name
        user = await db["users"].find_one({"_id": user_oid})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Decrypt full_name
        decrypted_full_name = safe_decrypt(fernet, user["full_name"])

        # Create a TransactionModel instance
        transaction_model = TransactionModel(
            user_id=user_oid,
            full_name=decrypted_full_name,
            transaction_amount=transaction.transaction_amount,
            transaction_type=transaction.transaction_type,
        )

        # Exclude 'id' when dumping the model to a dict
        transaction_dict = transaction_model.model_dump(by_alias=True, exclude={"id"})

        # Insert the transaction into the database
        result = await db["transactions"].insert_one(transaction_dict)
        created_transaction = await db["transactions"].find_one({"_id": result.inserted_id})

        if created_transaction:
            # Prepare the response
            created_transaction["id"] = str(created_transaction["_id"])
            created_transaction["user_id"] = str(created_transaction["user_id"])
            del created_transaction["_id"]
            return TransactionResponse(**created_transaction)
        else:
            raise HTTPException(status_code=500, detail="Transaction creation failed")

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
