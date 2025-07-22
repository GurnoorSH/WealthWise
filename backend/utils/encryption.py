from cryptography.fernet import Fernet
from config import settings
import base64


class AESEncryption:
    def __init__(self):
        # Use Fernet which provides AES-256 encryption
        self.cipher = Fernet(base64.urlsafe_b64encode(settings.encryption_key_bytes))
    
    def encrypt(self, data: str) -> str:
        """Encrypt a string and return base64 encoded result"""
        encrypted_data = self.cipher.encrypt(data.encode())
        return base64.b64encode(encrypted_data).decode()
    
    def decrypt(self, encrypted_data: str) -> str:
        """Decrypt base64 encoded encrypted data"""
        decoded_data = base64.b64decode(encrypted_data.encode())
        decrypted_data = self.cipher.decrypt(decoded_data)
        return decrypted_data.decode()


# Global instance
encryption = AESEncryption()
