from cryptography.fernet import Fernet


def get_encryption_key():
    """Generates and retrieves the encryption key for Fernet."""

    encryption_key = Fernet.generate_key().decode()
    
    return encryption_key
