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


# Get a user's transaction history
@router.get("/users/{user_id}/transactions/", response_model=List[TransactionResponse])
async def get_user_transactions(user_id: str, db=Depends(get_database)):
    try:
        # Convert user_id to ObjectId
        try:
            user_oid = ObjectId(user_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        # Find the user to get full_name
        user = await db["users"].find_one({"_id": user_oid})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Decrypt full_name
        decrypted_full_name = safe_decrypt(fernet, user["full_name"])

        # Find transactions for the user
        transactions = await db["transactions"].find({"user_id": user_oid}).to_list(length=None)

        transaction_responses = []
        for transaction in transactions:
            transaction["id"] = str(transaction["_id"])
            transaction["user_id"] = str(transaction["user_id"])
            del transaction["_id"]
            transaction["full_name"] = decrypted_full_name  # Ensure consistent full_name
            transaction_responses.append(TransactionResponse(**transaction))

        return transaction_responses

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# Update a transaction record
@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str, transaction_update: TransactionUpdate, db=Depends(get_database)
):
    try:
        # Convert transaction_id to ObjectId
        try:
            transaction_oid = ObjectId(transaction_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid transaction ID format")

        # Build the update document
        update_data = transaction_update.model_dump(exclude_unset=True)

        if not update_data:
            raise HTTPException(status_code=400, detail="No fields to update")

        # Update the transaction
        result = await db["transactions"].update_one(
            {"_id": transaction_oid},
            {"$set": update_data}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")

        # Retrieve the updated transaction
        updated_transaction = await db["transactions"].find_one({"_id": transaction_oid})

        # Get the user's full_name
        user = await db["users"].find_one({"_id": updated_transaction["user_id"]})
        decrypted_full_name = safe_decrypt(fernet, user["full_name"])

        # Prepare the response
        updated_transaction["id"] = str(updated_transaction["_id"])
        updated_transaction["user_id"] = str(updated_transaction["user_id"])
        del updated_transaction["_id"]
        updated_transaction["full_name"] = decrypted_full_name
        return TransactionResponse(**updated_transaction)

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

# Delete a transaction record
@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str, db=Depends(get_database)):
    try:
        # Convert transaction_id to ObjectId
        try:
            transaction_oid = ObjectId(transaction_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid transaction ID format")

        # Delete the transaction
        result = await db["transactions"].delete_one({"_id": transaction_oid})

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return {"message": "Transaction deleted successfully"}

    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
