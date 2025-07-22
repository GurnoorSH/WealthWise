from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app.models import User
from app.schemas import ExportResponse
from app.services.portfolio_service import portfolio_service
from app.utils.auth import get_current_user
from app.utils.encryption import encryption
import csv
import json
import io
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/export", tags=["export"])


@router.get("/csv")
async def export_csv(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export user's portfolio data as CSV"""
    try:
        # Get user's portfolios with valuations
        portfolios = await portfolio_service.get_user_portfolios_with_valuations(db, current_user.id)
        
        # Create CSV data
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write header
        writer.writerow([
            'Portfolio Name',
            'Asset Symbol',
            'Asset Name',
            'Asset Type',
            'Quantity',
            'Purchase Price',
            'Purchase Date',
            'Current Price',
            'Current Value',
            'Gain/Loss',
            'Gain/Loss %'
        ])
        
        # Write data rows
        for portfolio in portfolios:
            for asset in portfolio.assets:
                purchase_price = float(asset.purchase_price) if hasattr(asset, 'purchase_price') else 0
                current_price = float(asset.current_price) if hasattr(asset, 'current_price') and asset.current_price else 0
                current_value = float(asset.current_value) if hasattr(asset, 'current_value') and asset.current_value else 0
                purchase_value = purchase_price * float(asset.quantity)
                
                gain_loss = current_value - purchase_value
                gain_loss_percent = (gain_loss / purchase_value * 100) if purchase_value > 0 else 0
                
                writer.writerow([
                    portfolio.name,
                    asset.symbol,
                    asset.name,
                    asset.asset_type,
                    float(asset.quantity),
                    purchase_price,
                    asset.purchase_date.strftime('%Y-%m-%d'),
                    current_price if current_price > 0 else 'N/A',
                    current_value if current_value > 0 else 'N/A',
                    f"{gain_loss:.2f}" if current_value > 0 else 'N/A',
                    f"{gain_loss_percent:.2f}%" if current_value > 0 else 'N/A'
                ])
        
        output.seek(0)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"wealthwise_portfolio_{timestamp}.csv"
        
        return StreamingResponse(
            io.BytesIO(output.getvalue().encode('utf-8')),
            media_type="text/csv",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting CSV for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting data"
        )


@router.get("/json")
async def export_json(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Export user's portfolio data as JSON"""
    try:
        # Get user's portfolios with valuations
        portfolios = await portfolio_service.get_user_portfolios_with_valuations(db, current_user.id)
        
        # Build JSON structure
        export_data = {
            "user": {
                "id": current_user.id,
                "email": current_user.email,
                "full_name": current_user.full_name
            },
            "export_timestamp": datetime.now().isoformat(),
            "portfolios": []
        }
        
        total_current_value = 0
        total_purchase_value = 0
        
        for portfolio in portfolios:
            portfolio_data = {
                "id": portfolio.id,
                "name": portfolio.name,
                "description": portfolio.description,
                "created_at": portfolio.created_at.isoformat(),
                "assets": []
            }
            
            portfolio_current_value = 0
            portfolio_purchase_value = 0
            
            for asset in portfolio.assets:
                purchase_price = float(asset.purchase_price) if hasattr(asset, 'purchase_price') else 0
                current_price = float(asset.current_price) if hasattr(asset, 'current_price') and asset.current_price else None
                current_value = float(asset.current_value) if hasattr(asset, 'current_value') and asset.current_value else None
                purchase_value = purchase_price * float(asset.quantity)
                
                if current_value:
                    portfolio_current_value += current_value
                portfolio_purchase_value += purchase_value
                
                asset_data = {
                    "id": asset.id,
                    "symbol": asset.symbol,
                    "name": asset.name,
                    "asset_type": asset.asset_type,
                    "quantity": float(asset.quantity),
                    "purchase_price": purchase_price,
                    "purchase_date": asset.purchase_date.isoformat(),
                    "purchase_value": purchase_value,
                    "current_price": current_price,
                    "current_value": current_value,
                    "metadata": asset.metadata
                }
                
                if current_value and purchase_value > 0:
                    asset_data["gain_loss"] = current_value - purchase_value
                    asset_data["gain_loss_percent"] = (current_value - purchase_value) / purchase_value * 100
                
                portfolio_data["assets"].append(asset_data)
            
            portfolio_data["summary"] = {
                "total_assets": len(portfolio.assets),
                "purchase_value": portfolio_purchase_value,
                "current_value": portfolio_current_value,
                "gain_loss": portfolio_current_value - portfolio_purchase_value if portfolio_current_value else None,
                "gain_loss_percent": ((portfolio_current_value - portfolio_purchase_value) / portfolio_purchase_value * 100) if portfolio_purchase_value > 0 and portfolio_current_value else None
            }
            
            total_current_value += portfolio_current_value
            total_purchase_value += portfolio_purchase_value
            
            export_data["portfolios"].append(portfolio_data)
        
        # Add overall summary
        export_data["summary"] = {
            "total_portfolios": len(portfolios),
            "total_purchase_value": total_purchase_value,
            "total_current_value": total_current_value,
            "total_gain_loss": total_current_value - total_purchase_value if total_current_value else None,
            "total_gain_loss_percent": ((total_current_value - total_purchase_value) / total_purchase_value * 100) if total_purchase_value > 0 and total_current_value else None
        }
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"wealthwise_portfolio_{timestamp}.json"
        
        json_str = json.dumps(export_data, indent=2, default=str)
        
        return StreamingResponse(
            io.BytesIO(json_str.encode('utf-8')),
            media_type="application/json",
            headers={"Content-Disposition": f"attachment; filename={filename}"}
        )
        
    except Exception as e:
        logger.error(f"Error exporting JSON for user {current_user.id}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error exporting data"
        )
