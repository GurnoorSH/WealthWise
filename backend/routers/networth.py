from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List
from database import get_db
from models import User, NetWorthSnapshot
from schemas import NetWorthCurrent, NetWorthHistoryResponse, NetWorthHistory
from services.portfolio_service import portfolio_service
from services.price_service import price_service
from utils.auth import get_current_user
from utils.encryption import encryption
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/networth", tags=["net worth"])


@router.get("/current", response_model=NetWorthCurrent)
async def get_current_networth(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get current net worth for the user"""
    try:
        # Get user's portfolios with current valuations
        portfolios = await portfolio_service.get_user_portfolios_with_valuations(db, current_user.id)
        
        total_value = Decimal('0')
        portfolio_breakdown = {}
        
        for portfolio in portfolios:
            portfolio_value = Decimal('0')
            asset_breakdown = []
            
            for asset in portfolio.assets:
                current_value = Decimal('0')
                current_price = None
                
                if hasattr(asset, 'current_price') and asset.current_price:
                    current_price = asset.current_price
                    current_value = asset.quantity * current_price
                    portfolio_value += current_value
                
                asset_breakdown.append({
                    'symbol': asset.symbol,
                    'name': asset.name,
                    'asset_type': asset.asset_type,
                    'quantity': float(asset.quantity),
                    'purchase_price': float(asset.purchase_price) if hasattr(asset, 'purchase_price') else 0,
                    'current_price': float(current_price) if current_price else None,
                    'current_value': float(current_value),
                    'purchase_date': asset.purchase_date.isoformat()
                })
            
            total_value += portfolio_value
            portfolio_breakdown[portfolio.name] = {
                'id': portfolio.id,
                'value': float(portfolio_value),
                'assets': asset_breakdown
            }
        
        # Get the latest snapshot timestamp
        latest_snapshot = db.query(NetWorthSnapshot).filter(
            NetWorthSnapshot.user_id == current_user.id
        ).order_by(desc(NetWorthSnapshot.timestamp)).first()
        
        last_updated = latest_snapshot.timestamp if latest_snapshot else None
        
        return NetWorthCurrent(
            total_value=total_value,
            portfolio_breakdown=portfolio_breakdown,
            last_updated=last_updated
        )
        
    except Exception as e:
        logger.error(f"Error calculating current net worth for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error calculating net worth"
        )


@router.get("/history", response_model=NetWorthHistoryResponse)
def get_networth_history(
    days: int = 30,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get net worth history for the user"""
    try:
        # Get historical snapshots
        snapshots = db.query(NetWorthSnapshot).filter(
            NetWorthSnapshot.user_id == current_user.id
        ).order_by(desc(NetWorthSnapshot.timestamp)).limit(days).all()
        
        history = []
        for snapshot in reversed(snapshots):  # Reverse to get chronological order
            history.append(NetWorthHistory(
                timestamp=snapshot.timestamp,
                total_value=snapshot.total_value,
                portfolio_breakdown=snapshot.portfolio_breakdown
            ))
        
        return NetWorthHistoryResponse(history=history)
        
    except Exception as e:
        logger.error(f"Error fetching net worth history for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error fetching net worth history"
        )
