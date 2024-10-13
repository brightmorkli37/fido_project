from cryptography.fernet import Fernet
import os

key = os.getenv('FERNET_KEY')  # Ensure to generate and store this key securely.
cipher_suite = Fernet(key)

def encrypt_data(data: str) -> str:
    return cipher_suite.encrypt(data.encode()).decode()

def decrypt_data(encrypted_data: str) -> str:
    return cipher_suite.decrypt(encrypted_data.encode()).decode()
