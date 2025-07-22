from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from decimal import Decimal
from app.models import Portfolio, Asset, User
from app.schemas import PortfolioCreate, AssetCreate
from app.utils.encryption import encryption
from app.services.price_service import price_service
import logging

logger = logging.getLogger(__name__)


class PortfolioService:
    def create_portfolio(self, db: Session, portfolio: PortfolioCreate, user_id: int) -> Portfolio:
        """Create a new portfolio"""
        db_portfolio = Portfolio(
            name=portfolio.name,
            description=portfolio.description,
            user_id=user_id
        )
        db.add(db_portfolio)
        db.commit()
        db.refresh(db_portfolio)
        return db_portfolio
    
    def get_user_portfolios(self, db: Session, user_id: int) -> List[Portfolio]:
        """Get all portfolios for a user"""
        return db.query(Portfolio).filter(Portfolio.user_id == user_id).all()
    
    def get_portfolio_by_id(self, db: Session, portfolio_id: int, user_id: int) -> Optional[Portfolio]:
        """Get a specific portfolio by ID for a user"""
        return db.query(Portfolio).filter(
            and_(Portfolio.id == portfolio_id, Portfolio.user_id == user_id)
        ).first()
    
    async def get_user_portfolios_with_valuations(self, db: Session, user_id: int) -> List[Portfolio]:
        """Get user portfolios with current asset valuations"""
        portfolios = self.get_user_portfolios(db, user_id)
        
        for portfolio in portfolios:
            # Load assets for each portfolio
            portfolio.assets = db.query(Asset).filter(Asset.portfolio_id == portfolio.id).all()
            
            # Add current price and value to each asset
            for asset in portfolio.assets:
                latest_price = price_service.get_latest_price(db, asset.symbol, asset.asset_type)
                if latest_price:
                    asset.current_price = latest_price.price
                    asset.current_value = asset.quantity * latest_price.price
                else:
                    asset.current_price = None
                    asset.current_value = None
                
                # Decrypt purchase price for display
                try:
                    asset.purchase_price = Decimal(encryption.decrypt(asset.purchase_price_encrypted))
                except Exception as e:
                    logger.error(f"Error decrypting purchase price for asset {asset.id}: {e}")
                    asset.purchase_price = Decimal('0')
        
        return portfolios
    
    def create_asset(self, db: Session, asset: AssetCreate, portfolio_id: int, user_id: int) -> Optional[Asset]:
        """Create a new asset in a portfolio"""
        # Verify portfolio belongs to user
        portfolio = self.get_portfolio_by_id(db, portfolio_id, user_id)
        if not portfolio:
            return None
        
        # Encrypt purchase price
        encrypted_price = encryption.encrypt(str(asset.purchase_price))
        
        db_asset = Asset(
            symbol=asset.symbol.upper(),
            name=asset.name,
            asset_type=asset.asset_type,
            quantity=asset.quantity,
            purchase_price_encrypted=encrypted_price,
            purchase_date=asset.purchase_date,
            portfolio_id=portfolio_id,
            metadata=asset.metadata
        )
        
        db.add(db_asset)
        db.commit()
        db.refresh(db_asset)
        
        # Set decrypted purchase price for response
        db_asset.purchase_price = asset.purchase_price
        
        return db_asset
    
    def get_portfolio_assets(self, db: Session, portfolio_id: int, user_id: int) -> List[Asset]:
        """Get all assets in a portfolio"""
        # Verify portfolio belongs to user
        portfolio = self.get_portfolio_by_id(db, portfolio_id, user_id)
        if not portfolio:
            return []
        
        assets = db.query(Asset).filter(Asset.portfolio_id == portfolio_id).all()
        
        # Decrypt purchase prices and add current valuations
        for asset in assets:
            try:
                asset.purchase_price = Decimal(encryption.decrypt(asset.purchase_price_encrypted))
            except Exception as e:
                logger.error(f"Error decrypting purchase price for asset {asset.id}: {e}")
                asset.purchase_price = Decimal('0')
            
            # Add current price and value
            latest_price = price_service.get_latest_price(db, asset.symbol, asset.asset_type)
            if latest_price:
                asset.current_price = latest_price.price
                asset.current_value = asset.quantity * latest_price.price
            else:
                asset.current_price = None
                asset.current_value = None
        
        return assets
    
    def update_portfolio(self, db: Session, portfolio_id: int, portfolio_update: dict, user_id: int) -> Optional[Portfolio]:
        """Update a portfolio"""
        portfolio = self.get_portfolio_by_id(db, portfolio_id, user_id)
        if not portfolio:
            return None
        
        for key, value in portfolio_update.items():
            if hasattr(portfolio, key):
                setattr(portfolio, key, value)
        
        db.commit()
        db.refresh(portfolio)
        return portfolio
    
    def delete_portfolio(self, db: Session, portfolio_id: int, user_id: int) -> bool:
        """Delete a portfolio and all its assets"""
        portfolio = self.get_portfolio_by_id(db, portfolio_id, user_id)
        if not portfolio:
            return False
        
        # Delete all assets first
        db.query(Asset).filter(Asset.portfolio_id == portfolio_id).delete()
        
        # Delete portfolio
        db.delete(portfolio)
        db.commit()
        return True


portfolio_service = PortfolioService()
