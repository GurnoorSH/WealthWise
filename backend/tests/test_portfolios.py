import pytest
from datetime import datetime
from decimal import Decimal


def test_create_portfolio(authenticated_client):
    """Test creating a portfolio"""
    portfolio_data = {
        "name": "My Investment Portfolio",
        "description": "Long-term investments"
    }
    
    response = authenticated_client.post("/portfolios/", json=portfolio_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == portfolio_data["name"]
    assert data["description"] == portfolio_data["description"]
    assert "id" in data


def test_get_portfolios(authenticated_client):
    """Test getting user portfolios"""
    # Create a portfolio first
    portfolio_data = {
        "name": "Test Portfolio",
        "description": "Test description"
    }
    authenticated_client.post("/portfolios/", json=portfolio_data)
    
    # Get portfolios
    response = authenticated_client.get("/portfolios/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == portfolio_data["name"]


def test_create_asset(authenticated_client):
    """Test adding an asset to a portfolio"""
    # Create portfolio first
    portfolio_data = {
        "name": "Stock Portfolio",
        "description": "My stocks"
    }
    portfolio_response = authenticated_client.post("/portfolios/", json=portfolio_data)
    portfolio_id = portfolio_response.json()["id"]
    
    # Add asset
    asset_data = {
        "symbol": "AAPL",
        "name": "Apple Inc.",
        "asset_type": "stock",
        "quantity": "10.5",
        "purchase_price": "150.25",
        "purchase_date": "2024-01-15T10:30:00"
    }
    
    response = authenticated_client.post(f"/portfolios/{portfolio_id}/assets", json=asset_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["symbol"] == asset_data["symbol"]
    assert data["name"] == asset_data["name"]
    assert data["asset_type"] == asset_data["asset_type"]
    assert float(data["quantity"]) == float(asset_data["quantity"])


def test_get_portfolio_assets(authenticated_client):
    """Test getting assets from a portfolio"""
    # Create portfolio and asset
    portfolio_data = {"name": "Test Portfolio"}
    portfolio_response = authenticated_client.post("/portfolios/", json=portfolio_data)
    portfolio_id = portfolio_response.json()["id"]
    
    asset_data = {
        "symbol": "BTC",
        "name": "Bitcoin",
        "asset_type": "crypto",
        "quantity": "0.5",
        "purchase_price": "45000.00",
        "purchase_date": "2024-01-15T10:30:00"
    }
    authenticated_client.post(f"/portfolios/{portfolio_id}/assets", json=asset_data)
    
    # Get assets
    response = authenticated_client.get(f"/portfolios/{portfolio_id}/assets")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["symbol"] == asset_data["symbol"]


def test_unauthorized_access(client):
    """Test accessing portfolios without authentication"""
    response = client.get("/portfolios/")
    assert response.status_code == 401
