from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from app.schemas import TransactionCreate, TransactionResponse
from app.models import TransactionModel
from db.mongodb import get_database

router = APIRouter()

@router.post("/users/{user_id}/transactions/", response_model=TransactionResponse)
async def create_transaction(user_id: str, transaction: TransactionCreate, db=Depends(get_database)):
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    
    transaction_dict = transaction.dict()
    transaction_dict["user_id"] = ObjectId(user_id)
    result = await db["transactions"].insert_one(transaction_dict)
    created_transaction = await db["transactions"].find_one({"_id": result.inserted_id})
    return TransactionModel(**created_transaction)

@router.get("/users/{user_id}/transactions/", response_model=List[TransactionResponse])
async def read_user_transactions(user_id: str, db=Depends(get_database)):
    transactions = await db["transactions"].find({"user_id": ObjectId(user_id)}).to_list(1000)
    return [TransactionModel(**t) for t in transactions]

@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(transaction_id: str, transaction: TransactionCreate, db=Depends(get_database)):
    transaction_dict = transaction.dict()
    result = await db["transactions"].update_one(
        {"_id": ObjectId(transaction_id)},
        {"$set": transaction_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    updated_transaction = await db["transactions"].find_one({"_id": ObjectId(transaction_id)})
    return TransactionModel(**updated_transaction)

@router.delete("/transactions/{transaction_id}")
async def delete_transaction(transaction_id: str, db=Depends(get_database)):
    result = await db["transactions"].delete_one({"_id": ObjectId(transaction_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return {"message": "Transaction deleted successfully"}

@router.get("/users/{user_id}/analytics")
async def get_user_analytics(user_id: str, db=Depends(get_database)):
    pipeline = [
        {"$match": {"user_id": ObjectId(user_id)}},
        {"$group": {
            "_id": None,
            "avg_value": {"$avg": "$transaction_amount"},
            "total_transactions": {"$sum": 1},
            "transactions": {"$push": {"date": "$transaction_date", "amount": "$transaction_amount"}}
        }}
    ]
    result = await db["transactions"].aggregate(pipeline).to_list(1)
    
    if not result:
        raise HTTPException(status_code=404, detail="No transactions found for this user")
    
    analytics = result[0]
    transactions = analytics["transactions"]
    
    date_counts = {}
    for t in transactions:
        date = t["date"].date()
        date_counts[date] = date_counts.get(date, 0) + 1
    
    most_active_day = max(date_counts, key=date_counts.get)
    
    return {
        "average_transaction_value": analytics["avg_value"],
        "most_active_day": most_active_day,
        "total_transactions": analytics["total_transactions"]
    }