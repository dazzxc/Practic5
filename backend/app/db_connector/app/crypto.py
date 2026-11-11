import base64
import hashlib
from cryptography.fernet import Fernet 
from app.config import settings

class CryptoManager:
    def __init__(self):
        key_material = hashlib.sha256(settings.secret_key.encode()).digest()
        fernet_key = base64.urlsafe_b64encode(key_material)
        self.cipher = Fernet(fernet_key)
    def encrypt(self, password: str) -> str:
        if not password:
            return""
        encrypted_bytes = self.cipher.encrypt(password.encode())
        return encrypted_bytes.decode()
    def decrypt(self, encrypted_password: str) -> str:
        if not encrypted_password:
            return ""
        decrypted_bytes = self.cipher.decrypt(encrypted_password.encode())
        return decrypted_bytes.decode()

crypto = CryptoManager()