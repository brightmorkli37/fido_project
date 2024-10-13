from fastapi import APIRouter, HTTPException, Depends
from typing import List
from bson import ObjectId
from bson.errors import InvalidId
from app.api_v1.schemas import UserCreate, UserResponse
from app.api_v1.models import UserModel
from db.database import get_database
from cryptography.fernet import Fernet
from app.api_v1.utils import generate_key
from app.api_v1.utils.encrypt_decrypt import safe_encrypt, safe_decrypt

router = APIRouter()

ENCRYPTION_KEY = generate_key.get_encryption_key()
fernet = Fernet(ENCRYPTION_KEY.encode())

# routes.py

@router.post("/users/", response_model=UserResponse)
async def create_user(user: UserCreate, db=Depends(get_database)):
    try:
        encrypted_name = safe_encrypt(fernet, user.full_name)

        # Create an instance of UserModel
        user_model = UserModel(full_name=encrypted_name)

        # Dump the model to a dict without excluding unset fields
        user_dict = user_model.model_dump(by_alias=True, exclude={"id"})

        # Insert the user into the database
        result = await db["users"].insert_one(user_dict)

        # Retrieve the inserted user
        created_user = await db["users"].find_one({"_id": result.inserted_id})

        if created_user:
            # Decrypt the full_name before returning
            created_user["full_name"] = safe_decrypt(fernet, created_user["full_name"])
            # Map '_id' to 'id' and convert to string
            created_user["id"] = str(created_user["_id"])
            del created_user["_id"]
            return UserResponse(**created_user)
        else:
            raise HTTPException(status_code=404, detail="User not found after creation")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


@router.get("/users/{user_id}", response_model=UserResponse)
async def read_user(user_id: str, db=Depends(get_database)):
    try:
        # Convert the user_id string to a MongoDB ObjectId
        try:
            oid = ObjectId(user_id)
        except InvalidId:
            raise HTTPException(status_code=400, detail="Invalid user ID format")

        # Find the user in the database
        user = await db["users"].find_one({"_id": oid})

        if not user:
            raise HTTPException(status_code=404, detail="User not found")

       
        # Map '_id' to 'id' and convert to string
        user_response = UserResponse(
            id=str(user["_id"]),
            full_name=user["full_name"],
            created_at=user["created_at"]
        )

        return user_response

    except HTTPException as e:
        # Re-raise HTTP exceptions to be handled by FastAPI
        raise e
    except Exception as e:
        # Catch any other exceptions and return a 500 error
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")



@router.get("/users/", response_model=List[UserResponse])
async def read_users(skip: int = 0, limit: int = 10, db=Depends(get_database)):
    try:
        users = await db["users"].find().skip(skip).limit(limit).to_list(length=limit)
        
        user_responses = []
        for user in users:
            # Decrypt the full_name before adding to the response list
            user["full_name"] = safe_decrypt(fernet, user["full_name"])
            user["id"] = str(user["_id"])
            del user["_id"]
            user_responses.append(UserResponse(**user))
        
        return user_responses
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(user_id: str, user: UserCreate, db=Depends(get_database)):
    try:
        encrypted_name = safe_encrypt(fernet, user.full_name)
        # Prepare the update document
        update_data = {"full_name": encrypted_name}
        
        result = await db["users"].update_one(
            {"_id": ObjectId(user_id)},
            {"$set": update_data}
        )
        
        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
        
        updated_user["full_name"] = safe_decrypt(fernet, updated_user["full_name"])
        updated_user["id"] = str(updated_user["_id"])
        del updated_user["_id"]
        return UserResponse(**updated_user)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")

@router.delete("/users/{user_id}")
async def delete_user(user_id: str, db=Depends(get_database)):
    try:
        result = await db["users"].delete_one({"_id": ObjectId(user_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="User not found")
        
        return {"message": "User deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")
