from pydantic_settings import BaseSettings
from typing import Optional
import base64
import os


class Settings(BaseSettings):
    # Database
    database_url: str
    
    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 30
    
    # AES Encryption
    aes_encryption_key: str
    
    # API Keys
    alpha_vantage_api_key: str
    coingecko_api_key: Optional[str] = None
    
    # CORS
    vite_api_base_url: str = "http://localhost:3000"
    
    # App
    app_name: str = "WealthWise"
    app_version: str = "1.0.0"
    debug: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False
    
    @property
    def encryption_key_bytes(self) -> bytes:
        """Convert base64 encoded key to bytes"""
        return base64.b64decode(self.aes_encryption_key)


settings = Settings()
