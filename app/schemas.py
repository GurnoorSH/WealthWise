from pydantic import BaseModel, EmailStr
from typing import Optional, List, Dict, Any
from datetime import datetime
from decimal import Decimal


# User Schemas
class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class User(UserBase):
    id: int
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


# Portfolio Schemas
class PortfolioBase(BaseModel):
    name: str
    description: Optional[str] = None


class PortfolioCreate(PortfolioBase):
    pass


class Portfolio(PortfolioBase):
    id: int
    user_id: int
    created_at: datetime
    updated_at: Optional[datetime]
    
    class Config:
        from_attributes = True


class PortfolioWithAssets(Portfolio):
    assets: List['Asset'] = []


# Asset Schemas
class AssetBase(BaseModel):
    symbol: str
    name: str
    asset_type: str
    quantity: Decimal
    purchase_price: Decimal
    purchase_date: datetime
    metadata: Optional[Dict[str, Any]] = None


class AssetCreate(AssetBase):
    pass


class Asset(BaseModel):
    id: int
    symbol: str
    name: str
    asset_type: str
    quantity: Decimal
    purchase_price: Decimal
    purchase_date: datetime
    portfolio_id: int
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime]
    current_price: Optional[Decimal] = None
    current_value: Optional[Decimal] = None
    
    class Config:
        from_attributes = True


# Net Worth Schemas
class NetWorthCurrent(BaseModel):
    total_value: Decimal
    portfolio_breakdown: Dict[str, Any]
    last_updated: datetime


class NetWorthHistory(BaseModel):
    timestamp: datetime
    total_value: Decimal
    portfolio_breakdown: Dict[str, Any]


class NetWorthHistoryResponse(BaseModel):
    history: List[NetWorthHistory]


# Price Snapshot Schema
class PriceSnapshot(BaseModel):
    symbol: str
    asset_type: str
    price: Decimal
    currency: str
    timestamp: datetime
    source: str
    
    class Config:
        from_attributes = True


# Export Schemas
class ExportResponse(BaseModel):
    message: str
    download_url: Optional[str] = None
