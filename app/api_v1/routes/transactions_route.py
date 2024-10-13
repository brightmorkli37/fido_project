from fastapi import APIRouter, HTTPException
from app.api_v1.schemas import TransactionCreate
from app.services.encryption_service import encrypt_data, decrypt_data
from db.database import transaction_collection, user_collection
from bson import ObjectId
from collections import Counter


router = APIRouter()

@router.post("/transactions/")
async def create_transaction(user_id: str, transaction: TransactionCreate):
    user = await user_collection.find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    transaction_dict = transaction.model_dump()
    transaction_dict['user_id'] = user_id
    transaction_dict['full_name'] = encrypt_data(user['full_name'])
    result = await transaction_collection.insert_one(transaction_dict)
    return {"inserted_id": str(result.inserted_id)}

@router.get("/transactions/{user_id}")
async def get_transaction_history(user_id: str):
    transactions = await transaction_collection.find({"user_id": user_id}).to_list(length=100)
    if transactions:
        for tx in transactions:
            tx['full_name'] = decrypt_data(tx['full_name'])
        return transactions
    raise HTTPException(status_code=404, detail="No transactions found")



@router.get("/analytics/{user_id}")
async def get_transaction_analytics(user_id: str):
    transactions = await transaction_collection.find({"user_id": user_id}).to_list(length=1000)
    if not transactions:
        raise HTTPException(status_code=404, detail="No transactions found")

    # Average Transaction Value
    total_amount = sum(tx['transaction_amount'] for tx in transactions)
    avg_transaction_value = total_amount / len(transactions)

    # Day with Highest Transactions
    dates = [tx['transaction_date'].date() for tx in transactions]
    most_common_date = Counter(dates).most_common(1)[0]

    return {
        "average_transaction_value": avg_transaction_value,
        "highest_transactions_day": most_common_date[0].isoformat()
    }

