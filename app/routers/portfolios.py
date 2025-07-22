from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import Portfolio, PortfolioCreate, PortfolioWithAssets, Asset, AssetCreate
from app.services.portfolio_service import portfolio_service
from app.utils.auth import get_current_user

router = APIRouter(prefix="/portfolios", tags=["portfolios"])


@router.post("/", response_model=Portfolio)
def create_portfolio(
    portfolio: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Create a new portfolio"""
    return portfolio_service.create_portfolio(db, portfolio, current_user.id)


@router.get("/", response_model=List[PortfolioWithAssets])
async def get_portfolios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all portfolios for the current user with asset valuations"""
    return await portfolio_service.get_user_portfolios_with_valuations(db, current_user.id)


@router.get("/{portfolio_id}", response_model=PortfolioWithAssets)
def get_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get a specific portfolio"""
    portfolio = portfolio_service.get_portfolio_by_id(db, portfolio_id, current_user.id)
    if not portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    
    # Load assets
    portfolio.assets = portfolio_service.get_portfolio_assets(db, portfolio_id, current_user.id)
    return portfolio


@router.put("/{portfolio_id}", response_model=Portfolio)
def update_portfolio(
    portfolio_id: int,
    portfolio_update: PortfolioCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update a portfolio"""
    updated_portfolio = portfolio_service.update_portfolio(
        db, portfolio_id, portfolio_update.dict(exclude_unset=True), current_user.id
    )
    if not updated_portfolio:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    return updated_portfolio


@router.delete("/{portfolio_id}")
def delete_portfolio(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Delete a portfolio"""
    success = portfolio_service.delete_portfolio(db, portfolio_id, current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    return {"message": "Portfolio deleted successfully"}


@router.post("/{portfolio_id}/assets", response_model=Asset)
def create_asset(
    portfolio_id: int,
    asset: AssetCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Add an asset to a portfolio"""
    db_asset = portfolio_service.create_asset(db, asset, portfolio_id, current_user.id)
    if not db_asset:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Portfolio not found"
        )
    return db_asset


@router.get("/{portfolio_id}/assets", response_model=List[Asset])
def get_portfolio_assets(
    portfolio_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Get all assets in a portfolio"""
    assets = portfolio_service.get_portfolio_assets(db, portfolio_id, current_user.id)
    return assets
