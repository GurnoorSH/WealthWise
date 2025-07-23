from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, DECIMAL, Boolean, Float
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    portfolios = relationship("Portfolio", back_populates="owner")


class Portfolio(Base):
    __tablename__ = "portfolios"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    owner = relationship("User", back_populates="portfolios")
    assets = relationship("Asset", back_populates="portfolio")


class Asset(Base):
    __tablename__ = "assets"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    name = Column(String, nullable=False)
    asset_type = Column(String, nullable=False)  # 'stock', 'crypto', 'bond', etc.
    quantity = Column(DECIMAL(20, 8), nullable=False)
    purchase_price_encrypted = Column(Text, nullable=False)  # AES encrypted
    purchase_date = Column(DateTime(timezone=True), nullable=False)
    portfolio_id = Column(Integer, ForeignKey("portfolios.id"), nullable=False)
    metadata = Column(JSONB, nullable=True)  # Additional asset metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    portfolio = relationship("Portfolio", back_populates="assets")


class PriceSnapshot(Base):
    __tablename__ = "price_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    asset_type = Column(String, nullable=False)
    price = Column(DECIMAL(20, 8), nullable=False)
    currency = Column(String, default="USD")
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    source = Column(String, nullable=False)  # 'alpha_vantage', 'coingecko'
    metadata = Column(JSONB, nullable=True)


class NetWorthSnapshot(Base):
    __tablename__ = "networth_snapshots"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    total_value = Column(DECIMAL(20, 2), nullable=False)
    portfolio_breakdown = Column(JSONB, nullable=False)  # Portfolio-wise breakdown
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    user = relationship("User")


class News(Base):
    __tablename__ = "news"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, nullable=False, index=True)
    title = Column(String, nullable=False)
    url = Column(String, nullable=False)
    source = Column(String, nullable=True)
    importance_score = Column(Float, nullable=False, default=0.0)
    timestamp = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    metadata = Column(JSONB, nullable=True)  # Additional news metadata
