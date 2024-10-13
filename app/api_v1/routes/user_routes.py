from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from schemas import UserCreate, UserResponse
from models import UserModel
from db.mongodb import get_database
from cryptography.fernet import Fernet
import os

router = APIRouter()

ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY").encode()
fernet = Fernet(ENCRYPTION_KEY)

@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db=Depends(get_database)):
    encrypted_name = fernet.encrypt(user.full_name.encode()).decode()
    user_dict = user.dict()
    user_dict["full_name"] = encrypted_name
    result = await db["users"].insert_one(user_dict)
    created_user = await db["users"].find_one({"_id": result.inserted_id})
    created_user["full_name"] = fernet.decrypt(created_user["full_name"].encode()).decode()
    return UserModel(**created_user)

@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: str, db=Depends(get_database)):
    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    user["full_name"] = fernet.decrypt(user["full_name"].encode()).decode()
    return UserModel(**user)

@router.get("/users/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 10, db=Depends(get_database)):
    users = await db["users"].find().skip(skip).limit(limit).to_list(limit)
    for user in users:
        user["full_name"] = fernet.decrypt(user["full_name"].encode()).decode()
    return [UserModel(**user) for user in users]

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserCreate, db=Depends(get_database)):
    encrypted_name = fernet.encrypt(user.full_name.encode()).decode()
    user_dict = user.dict()
    user_dict["full_name"] = encrypted_name
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": user_dict}
    )
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    updated_user["full_name"] = fernet.decrypt(updated_user["full_name"].encode()).decode()
    return UserModel(**updated_user)

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db=Depends(get_database)):
    result = await db["users"].delete_one({"_id": ObjectId(user_id)})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}