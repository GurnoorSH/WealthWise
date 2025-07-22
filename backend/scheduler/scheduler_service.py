from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from sqlalchemy.orm import Session
from sqlalchemy import distinct
from database import SessionLocal
from models import Asset, NetWorthSnapshot, User
from services.price_service import price_service
from utils.encryption import encryption
from decimal import Decimal
import logging
import asyncio

logger = logging.getLogger(__name__)


class SchedulerService:
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self.setup_jobs()
    
    def setup_jobs(self):
        """Setup scheduled jobs"""
        # Daily price fetch and valuation at 02:00
        self.scheduler.add_job(
            func=self.daily_price_update_job,
            trigger=CronTrigger(hour=2, minute=0),
            id='daily_price_update',
            name='Daily Price Update and Valuation',
            replace_existing=True
        )
    
    async def daily_price_update_job(self):
        """Daily job to fetch prices and compute valuations"""
        logger.info("Starting daily price update job")
        
        db = SessionLocal()
        try:
            # Get all unique symbols and asset types from assets
            unique_assets = db.query(
                distinct(Asset.symbol),
                Asset.asset_type
            ).all()
            
            # Fetch prices for all unique assets
            for symbol, asset_type in unique_assets:
                logger.info(f"Fetching price for {symbol} ({asset_type})")
                await price_service.fetch_and_store_price(db, symbol, asset_type)
                # Add small delay to avoid rate limiting
                await asyncio.sleep(1)
            
            # Compute and store net worth snapshots for all users
            await self.compute_all_user_valuations(db)
            
            logger.info("Daily price update job completed successfully")
            
        except Exception as e:
            logger.error(f"Error in daily price update job: {e}")
        finally:
            db.close()
    
    async def compute_all_user_valuations(self, db: Session):
        """Compute net worth for all users"""
        users = db.query(User).all()
        
        for user in users:
            try:
                await self.compute_user_net_worth(db, user.id)
            except Exception as e:
                logger.error(f"Error computing net worth for user {user.id}: {e}")
    
    async def compute_user_net_worth(self, db: Session, user_id: int):
        """Compute and store net worth snapshot for a user"""
        from services.portfolio_service import portfolio_service
        
        # Get user's portfolios with current valuations
        portfolios = await portfolio_service.get_user_portfolios_with_valuations(db, user_id)
        
        total_value = Decimal('0')
        portfolio_breakdown = {}
        
        for portfolio in portfolios:
            portfolio_value = Decimal('0')
            asset_breakdown = []
            
            for asset in portfolio.assets:
                # Get latest price
                latest_price = price_service.get_latest_price(db, asset.symbol, asset.asset_type)
                
                if latest_price:
                    current_value = asset.quantity * latest_price.price
                    portfolio_value += current_value
                    
                    asset_breakdown.append({
                        'symbol': asset.symbol,
                        'quantity': float(asset.quantity),
                        'current_price': float(latest_price.price),
                        'current_value': float(current_value),
                        'purchase_price': float(encryption.decrypt(asset.purchase_price_encrypted))
                    })
            
            total_value += portfolio_value
            portfolio_breakdown[portfolio.name] = {
                'value': float(portfolio_value),
                'assets': asset_breakdown
            }
        
        # Store net worth snapshot
        net_worth_snapshot = NetWorthSnapshot(
            user_id=user_id,
            total_value=total_value,
            portfolio_breakdown=portfolio_breakdown
        )
        
        db.add(net_worth_snapshot)
        db.commit()
        
        logger.info(f"Stored net worth snapshot for user {user_id}: ${total_value}")
    
    def start(self):
        """Start the scheduler"""
        if not self.scheduler.running:
            self.scheduler.start()
            logger.info("Scheduler started")
    
    def shutdown(self):
        """Shutdown the scheduler"""
        if self.scheduler.running:
            self.scheduler.shutdown()
            logger.info("Scheduler shutdown")


scheduler_service = SchedulerService()
