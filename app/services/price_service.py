import requests
from typing import Dict, Optional
from decimal import Decimal
from datetime import datetime
from sqlalchemy.orm import Session
from app.config import settings
from app.models import PriceSnapshot
import logging

logger = logging.getLogger(__name__)


class PriceService:
    def __init__(self):
        self.alpha_vantage_base_url = "https://www.alphavantage.co/query"
        self.coingecko_base_url = "https://api.coingecko.com/api/v3"
    
    async def fetch_stock_price(self, symbol: str) -> Optional[Dict]:
        """Fetch stock price from Alpha Vantage"""
        try:
            params = {
                'function': 'GLOBAL_QUOTE',
                'symbol': symbol,
                'apikey': settings.alpha_vantage_api_key
            }
            
            response = requests.get(self.alpha_vantage_base_url, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            if 'Global Quote' in data:
                quote = data['Global Quote']
                return {
                    'symbol': symbol,
                    'price': Decimal(quote['05. price']),
                    'currency': 'USD',
                    'source': 'alpha_vantage',
                    'metadata': {
                        'change': quote.get('09. change'),
                        'change_percent': quote.get('10. change percent'),
                        'volume': quote.get('06. volume')
                    }
                }
            else:
                logger.error(f"No quote data for symbol {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching stock price for {symbol}: {e}")
            return None
    
    async def fetch_crypto_price(self, symbol: str) -> Optional[Dict]:
        """Fetch crypto price from CoinGecko"""
        try:
            # Convert symbol to CoinGecko ID (simplified mapping)
            crypto_id_map = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'ADA': 'cardano',
                'DOT': 'polkadot',
                'LINK': 'chainlink',
                'LTC': 'litecoin',
                'XRP': 'ripple',
                'BCH': 'bitcoin-cash',
                'BNB': 'binancecoin',
                'SOL': 'solana'
            }
            
            crypto_id = crypto_id_map.get(symbol.upper(), symbol.lower())
            
            url = f"{self.coingecko_base_url}/simple/price"
            params = {
                'ids': crypto_id,
                'vs_currencies': 'usd',
                'include_24hr_change': 'true',
                'include_24hr_vol': 'true'
            }
            
            headers = {}
            if settings.coingecko_api_key:
                headers['X-CG-Demo-API-Key'] = settings.coingecko_api_key
            
            response = requests.get(url, params=params, headers=headers)
            response.raise_for_status()
            
            data = response.json()
            
            if crypto_id in data:
                price_data = data[crypto_id]
                return {
                    'symbol': symbol.upper(),
                    'price': Decimal(str(price_data['usd'])),
                    'currency': 'USD',
                    'source': 'coingecko',
                    'metadata': {
                        '24h_change': price_data.get('usd_24h_change'),
                        '24h_volume': price_data.get('usd_24h_vol')
                    }
                }
            else:
                logger.error(f"No price data for crypto {symbol}: {data}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching crypto price for {symbol}: {e}")
            return None
    
    async def fetch_and_store_price(self, db: Session, symbol: str, asset_type: str) -> Optional[PriceSnapshot]:
        """Fetch price and store in database"""
        try:
            price_data = None
            
            if asset_type.lower() == 'stock':
                price_data = await self.fetch_stock_price(symbol)
            elif asset_type.lower() == 'crypto':
                price_data = await self.fetch_crypto_price(symbol)
            
            if price_data:
                # Store in database
                price_snapshot = PriceSnapshot(
                    symbol=price_data['symbol'],
                    asset_type=asset_type,
                    price=price_data['price'],
                    currency=price_data['currency'],
                    source=price_data['source'],
                    metadata=price_data.get('metadata')
                )
                
                db.add(price_snapshot)
                db.commit()
                db.refresh(price_snapshot)
                
                return price_snapshot
            
            return None
            
        except Exception as e:
            logger.error(f"Error storing price for {symbol}: {e}")
            db.rollback()
            return None
    
    def get_latest_price(self, db: Session, symbol: str, asset_type: str) -> Optional[PriceSnapshot]:
        """Get latest price from database"""
        return db.query(PriceSnapshot).filter(
            PriceSnapshot.symbol == symbol,
            PriceSnapshot.asset_type == asset_type
        ).order_by(PriceSnapshot.timestamp.desc()).first()


price_service = PriceService()
