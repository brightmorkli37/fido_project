from cryptography.fernet import Fernet, InvalidToken
from fastapi import HTTPException

def safe_encrypt(fernet: Fernet, data: str) -> str:
    return fernet.encrypt(data.encode()).decode()

def safe_decrypt(fernet: Fernet, data: str) -> str:
    try:
        return fernet.decrypt(data.encode()).decode()
    except InvalidToken:
        # If decryption fails, return the original data
        return data