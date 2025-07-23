from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime

from database import get_db
from models import News
from schemas import NewsItem
from utils.auth import get_current_user
from schemas import User

router = APIRouter(prefix="/api/news", tags=["news"])


def classify_importance(importance_score: float) -> str:
    """Classify news importance based on score"""
    if importance_score > 0.8:
        return "critical"
    elif importance_score > 0.5:
        return "important"
    else:
        return "routine"


@router.get("", response_model=List[NewsItem])
async def get_news(
    symbols: str = Query(..., description="Comma-separated list of symbols"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get news articles for specified symbols.
    Returns the 20 most recent articles matching the provided symbols.
    """
    # Parse symbols from comma-separated string
    symbol_list = [symbol.strip().upper() for symbol in symbols.split(",") if symbol.strip()]
    
    if not symbol_list:
        raise HTTPException(status_code=400, detail="At least one symbol must be provided")
    
    # Query news articles for the specified symbols
    news_query = db.query(News).filter(
        News.symbol.in_(symbol_list)
    ).order_by(
        News.timestamp.desc()
    ).limit(20)
    
    news_articles = news_query.all()
    
    # Convert to response format with importance classification
    news_items = []
    for article in news_articles:
        news_item = NewsItem(
            id=article.id,
            symbol=article.symbol,
            title=article.title,
            url=article.url,
            source=article.source,
            importance=classify_importance(article.importance_score),
            timestamp=article.timestamp
        )
        news_items.append(news_item)
    
    return news_items
