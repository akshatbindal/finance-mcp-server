import yfinance as yf
import pytz
from datetime import datetime
from typing import Dict, Any
import logging

logger = logging.getLogger("finance-mcp")

def get_market_info(symbol: str) -> Dict[str, Any]:
    """Fetch market info directly from Yahoo Finance."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        return {
            'timezone': info.get('exchangeTimezoneName', 'UTC'),
            'timezone_short': info.get('exchangeTimezoneShortName', 'UTC'),
            'market_state': info.get('marketState', 'UNKNOWN'),
            'exchange': info.get('exchange', 'N/A'),
            'currency': info.get('currency', 'USD'),
            'gmt_offset': info.get('gmtOffSetMilliseconds', 0),
            'country': info.get('country', 'N/A')
        }
    except Exception as e:
        logger.warning(f"Could not get market info for {symbol}: {e}")
        return {
            'timezone': 'UTC',
            'timezone_short': 'UTC',
            'market_state': 'UNKNOWN',
            'exchange': 'N/A',
            'currency': 'USD',
            'gmt_offset': 0,
            'country': 'N/A'
        }

def create_timezone_info(symbol: str, data_timestamp: datetime = None) -> Dict[str, Any]:
    market_info = get_market_info(symbol)  # Internal call within the same module
    market_tz_name = market_info['timezone']
    market_tz = pytz.timezone(market_tz_name)
    
    # Use Yahoo's original timestamp if available, no local conversion
    if data_timestamp is None:
        data_timestamp = datetime.fromtimestamp(market_info.get('regularMarketTime', datetime.now().timestamp()), tz=market_tz)
    
    return {
        'market_timestamp': data_timestamp.isoformat(),
        'market_timezone': market_tz_name,
        'market_status': market_info['market_state'],
        'exchange': market_info['exchange']
    }

