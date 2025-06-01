#!/usr/bin/env python3
"""
Finance MCP Server
Provides stock market data and technical indicators through MCP protocol
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union
import pandas as pd
import yfinance as yf
import ta
from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,   
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)
import mcp.types as types

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("finance-mcp")

# Initialize the MCP server
server = Server("finance-mcp")

class FinanceDataProvider:
    """Main class for handling financial data operations"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = 300  # 5 minutes cache
    
    def _is_cache_valid(self, symbol: str, cache_type: str) -> bool:
        """Check if cached data is still valid"""
        cache_key = f"{symbol}_{cache_type}"
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp')
        if not cached_time:
            return False
            
        return (datetime.now() - cached_time).seconds < self.cache_duration
    
    def _get_cached_data(self, symbol: str, cache_type: str) -> Optional[Dict]:
        """Get cached data if valid"""
        cache_key = f"{symbol}_{cache_type}"
        if self._is_cache_valid(symbol, cache_type):
            return self.cache[cache_key]['data']
        return None
    
    def _set_cache_data(self, symbol: str, cache_type: str, data: Dict):
        """Cache data with timestamp"""
        cache_key = f"{symbol}_{cache_type}"
        self.cache[cache_key] = {
            'data': data,
            'timestamp': datetime.now()
        }
    
    def dict_keys_to_str(self, obj):
        if isinstance(obj, dict):
            return {str(k): self.dict_keys_to_str(v) for k, v in obj.items()}
        elif isinstance(obj, list):
            return [self.dict_keys_to_str(i) for i in obj]
        else:
            return obj
    
    async def get_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get basic stock information"""
        try:
            # Check cache first
            cached_data = self._get_cached_data(symbol, 'info')
            if cached_data:
                return cached_data
            
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract key information
            stock_info = {
                'symbol': symbol,
                'company_name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'current_price': info.get('regularMarketPrice', 'N/A'),
                'previous_close': info.get('regularMarketPreviousClose', 'N/A'),
                'day_high': info.get('dayHigh', 'N/A'),
                'day_low': info.get('dayLow', 'N/A'),
                'volume': info.get('regularMarketVolume', 'N/A'),
                'avg_volume': info.get('averageVolume', 'N/A'),
                'pe_ratio': info.get('forwardPE', 'N/A'),
                '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'beta': info.get('beta', 'N/A')
            }
            
            # Cache the data
            self._set_cache_data(symbol, 'info', stock_info)
            return stock_info
            
        except Exception as e:
            logger.error(f"Error getting stock info for {symbol}: {str(e)}")
            raise Exception(f"Failed to get stock info: {str(e)}")
    
    async def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, Any]:
        """Get historical stock data"""
        try:
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period, interval=interval)
            
            if hist.empty:
                raise Exception(f"No historical data found for {symbol}")
            
            # Convert to dictionary format
            historical_data = {
                'symbol': symbol,
                'period': period,
                'interval': interval,
                'data': []
            }
            
            for date, row in hist.iterrows():
                historical_data['data'].append({
                    'date': date.strftime('%Y-%m-%d'),
                    'open': float(row['Open']),
                    'high': float(row['High']),
                    'low': float(row['Low']),
                    'close': float(row['Close']),
                    'volume': int(row['Volume'])
                })
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            raise Exception(f"Failed to get historical data: {str(e)}")
    
    async def get_realtime_data(self, symbol: str) -> Dict[str, Any]:
        """Get real-time stock data"""
        try:
            # Check cache first (shorter cache for real-time data)
            cache_key = f"{symbol}_realtime"
            if cache_key in self.cache:
                cached_time = self.cache[cache_key].get('timestamp')
                if cached_time and (datetime.now() - cached_time).seconds < 60:  # 1 minute cache
                    return self.cache[cache_key]['data']
            
            ticker = yf.Ticker(symbol)
            
            # Get the most recent data
            hist = ticker.history(period="1d", interval="1m")
            if hist.empty:
                # Fallback to daily data
                hist = ticker.history(period="5d", interval="1d")
            
            if hist.empty:
                raise Exception(f"No real-time data available for {symbol}")
            
            latest = hist.iloc[-1]
            
            realtime_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'price': float(latest['Close']),
                'open': float(latest['Open']),
                'high': float(latest['High']),
                'low': float(latest['Low']),
                'volume': int(latest['Volume']),
                'change': float(latest['Close'] - latest['Open']),
                'change_percent': float(((latest['Close'] - latest['Open']) / latest['Open']) * 100)
            }
            
            # Cache the data
            self.cache[cache_key] = {
                'data': realtime_data,
                'timestamp': datetime.now()
            }
            
            return realtime_data
            
        except Exception as e:
            logger.error(f"Error getting real-time data for {symbol}: {str(e)}")
            raise Exception(f"Failed to get real-time data: {str(e)}")
    
    async def calculate_technical_indicators(self, symbol: str, period: str = "1y", indicators: List[str] = None) -> Dict[str, Any]:
        """Calculate technical indicators for a stock"""
        try:
            if indicators is None:
                indicators = ['sma_20', 'sma_50', 'rsi', 'macd', 'bollinger_bands']
            
            # Get historical data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            
            if hist.empty:
                raise Exception(f"No historical data found for {symbol}")
            
            results = {
                'symbol': symbol,
                'period': period,
                'indicators': {}
            }
            
            # Simple Moving Averages
            if 'sma_20' in indicators:
                results['indicators']['sma_20'] = ta.trend.sma_indicator(hist['Close'], window=20).iloc[-1]
            
            if 'sma_50' in indicators:
                results['indicators']['sma_50'] = ta.trend.sma_indicator(hist['Close'], window=50).iloc[-1]
            
            if 'sma_200' in indicators:
                results['indicators']['sma_200'] = ta.trend.sma_indicator(hist['Close'], window=200).iloc[-1]
            
            # Exponential Moving Averages
            if 'ema_12' in indicators:
                results['indicators']['ema_12'] = ta.trend.ema_indicator(hist['Close'], window=12).iloc[-1]
            
            if 'ema_26' in indicators:
                results['indicators']['ema_26'] = ta.trend.ema_indicator(hist['Close'], window=26).iloc[-1]
            
            # RSI (Relative Strength Index)
            if 'rsi' in indicators:
                rsi = ta.momentum.rsi(hist['Close'], window=14)
                results['indicators']['rsi'] = float(rsi.iloc[-1])
            
            # MACD
            if 'macd' in indicators:
                macd_line = ta.trend.macd(hist['Close'])
                macd_signal = ta.trend.macd_signal(hist['Close'])
                macd_histogram = ta.trend.macd_diff(hist['Close'])
                
                results['indicators']['macd'] = {
                    'macd_line': float(macd_line.iloc[-1]),
                    'signal_line': float(macd_signal.iloc[-1]),
                    'histogram': float(macd_histogram.iloc[-1])
                }
            
            # Bollinger Bands
            if 'bollinger_bands' in indicators:
                bb_high = ta.volatility.bollinger_hband(hist['Close'])
                bb_low = ta.volatility.bollinger_lband(hist['Close'])
                bb_middle = ta.volatility.bollinger_mavg(hist['Close'])
                
                results['indicators']['bollinger_bands'] = {
                    'upper_band': float(bb_high.iloc[-1]),
                    'lower_band': float(bb_low.iloc[-1]),
                    'middle_band': float(bb_middle.iloc[-1])
                }
            
            # Stochastic Oscillator
            if 'stochastic' in indicators:
                stoch_k = ta.momentum.stoch(hist['High'], hist['Low'], hist['Close'])
                stoch_d = ta.momentum.stoch_signal(hist['High'], hist['Low'], hist['Close'])
                
                results['indicators']['stochastic'] = {
                    'k_percent': float(stoch_k.iloc[-1]),
                    'd_percent': float(stoch_d.iloc[-1])
                }
            
            # Average True Range (ATR)
            if 'atr' in indicators:
                atr = ta.volatility.average_true_range(hist['High'], hist['Low'], hist['Close'])
                results['indicators']['atr'] = float(atr.iloc[-1])
            
            # Volume indicators
            if 'volume_sma' in indicators:
                volume_sma = ta.volume.volume_sma(hist['Close'], hist['Volume'])
                results['indicators']['volume_sma'] = float(volume_sma.iloc[-1])
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators for {symbol}: {str(e)}")
            raise Exception(f"Failed to calculate technical indicators: {str(e)}")

    async def get_fundamental_data(self, symbol: str) -> Dict[str, Any]:
        """Get fundamental financial data for a company"""
        try:
            # Check cache first
            cached_data = self._get_cached_data(symbol, 'fundamentals')
            if cached_data:
                return cached_data

            ticker = yf.Ticker(symbol)
            
            # Get financial statements
            income_stmt = ticker.income_stmt
            balance_sheet = ticker.balance_sheet
            cash_flow = ticker.cashflow
            
            # Get key statistics
            info = ticker.info
            
            fundamental_data = {
                'symbol': symbol,
                'company_name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 'N/A'),
                'enterprise_value': info.get('enterpriseValue', 'N/A'),
                'trailing_pe': info.get('trailingPE', 'N/A'),
                'forward_pe': info.get('forwardPE', 'N/A'),
                'peg_ratio': info.get('pegRatio', 'N/A'),
                'price_to_book': info.get('priceToBook', 'N/A'),
                'price_to_sales': info.get('priceToSalesTrailing12Months', 'N/A'),
                'dividend_yield': info.get('dividendYield', 'N/A'),
                'profit_margins': info.get('profitMargins', 'N/A'),
                'operating_margins': info.get('operatingMargins', 'N/A'),
                'return_on_equity': info.get('returnOnEquity', 'N/A'),
                'return_on_assets': info.get('returnOnAssets', 'N/A'),
                'revenue': info.get('totalRevenue', 'N/A'),
                'revenue_per_share': info.get('revenuePerShare', 'N/A'),
                'revenue_growth': info.get('revenueGrowth', 'N/A'),
                'gross_profits': info.get('grossProfits', 'N/A'),
                'free_cashflow': info.get('freeCashflow', 'N/A'),
                'operating_cashflow': info.get('operatingCashflow', 'N/A'),
                'earnings_growth': info.get('earningsGrowth', 'N/A'),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', 'N/A'),
                'earnings_annual_growth': info.get('earningsAnnualGrowth', 'N/A'),
                'earnings_yearly_growth': info.get('earningsYearlyGrowth', 'N/A'),
                'earnings_annual': info.get('earningsAnnual', 'N/A'),
                'earnings_yearly': info.get('earningsYearly', 'N/A'),
                'earnings_quarterly': info.get('earningsQuarterly', 'N/A'),
                'earnings_ttm': info.get('trailingEps', 'N/A'),
                'earnings_forward': info.get('forwardEps', 'N/A'),
                'earnings_ttm_growth': info.get('earningsGrowth', 'N/A'),
                'earnings_forward_growth': info.get('earningsQuarterlyGrowth', 'N/A'),
                'earnings_annual_growth': info.get('earningsAnnualGrowth', 'N/A'),
                'earnings_yearly_growth': info.get('earningsYearlyGrowth', 'N/A'),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', 'N/A'),
                'earnings_ttm_growth': info.get('earningsGrowth', 'N/A'),
                'earnings_forward_growth': info.get('earningsQuarterlyGrowth', 'N/A'),
                'earnings_annual_growth': info.get('earningsAnnualGrowth', 'N/A'),
                'earnings_yearly_growth': info.get('earningsYearlyGrowth', 'N/A'),
                'earnings_quarterly_growth': info.get('earningsQuarterlyGrowth', 'N/A'),
                'financial_statements': {
                    'income_statement': self.dict_keys_to_str(income_stmt.to_dict()) if not income_stmt.empty else {},
                    'balance_sheet': self.dict_keys_to_str(balance_sheet.to_dict()) if not balance_sheet.empty else {},
                    'cash_flow': self.dict_keys_to_str(cash_flow.to_dict()) if not cash_flow.empty else {}
                }
            }
            
            # Cache the data
            self._set_cache_data(symbol, 'fundamentals', fundamental_data)
            return fundamental_data
            
        except Exception as e:
            logger.error(f"Error getting fundamental data for {symbol}: {str(e)}")
            raise Exception(f"Failed to get fundamental data: {str(e)}")

    async def get_company_news(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """Get latest news about a company"""
        try:
            # Check cache first (shorter cache for news)
            cache_key = f"{symbol}_news"
            if cache_key in self.cache:
                cached_time = self.cache[cache_key].get('timestamp')
                if cached_time and (datetime.now() - cached_time).seconds < 300:  # 5 minutes cache
                    return self.cache[cache_key]['data']

            ticker = yf.Ticker(symbol)
            news = ticker.news

            if not news:
                return {
                    'symbol': symbol,
                    'news': [],
                    'message': 'No news available'
                }

            # Process and format news items
            formatted_news = []
            for item in news[:limit]:
                formatted_news.append({
                    'title': item.get('title', 'N/A'),
                    'publisher': item.get('publisher', 'N/A'),
                    'link': item.get('link', 'N/A'),
                    'published': item.get('providerPublishTime', 'N/A'),
                    'type': item.get('type', 'N/A'),
                    'summary': item.get('summary', 'N/A'),
                    'related_tickers': item.get('relatedTickers', []),
                    'sentiment': item.get('sentiment', 'N/A')
                })

            news_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'news': formatted_news
            }

            # Cache the data
            self.cache[cache_key] = {
                'data': news_data,
                'timestamp': datetime.now()
            }

            return news_data

        except Exception as e:
            logger.error(f"Error getting news for {symbol}: {str(e)}")
            raise Exception(f"Failed to get company news: {str(e)}")

# Initialize the finance data provider
finance_provider = FinanceDataProvider()

@server.list_resources()
async def handle_list_resources() -> list[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="finance://stocks/info",
            name="Stock Information",
            description="Get basic information about stocks",
            mimeType="application/json",
        ),
        Resource(
            uri="finance://stocks/historical",
            name="Historical Data",
            description="Get historical stock price data",
            mimeType="application/json",
        ),
        Resource(
            uri="finance://stocks/realtime",
            name="Real-time Data",
            description="Get real-time stock price data",
            mimeType="application/json",
        ),
        Resource(
            uri="finance://stocks/indicators",
            name="Technical Indicators",
            description="Calculate technical indicators for stocks",
            mimeType="application/json",
        ),
        Resource(
            uri="finance://stocks/fundamentals",
            name="Fundamental Data",
            description="Get fundamental financial data for stocks",
            mimeType="application/json",
        ),
        Resource(
            uri="finance://stocks/news",
            name="Company News",
            description="Get latest news about companies",
            mimeType="application/json",
        ),
    ]

@server.read_resource()
async def handle_read_resource(uri: types.AnyUrl) -> str:
    """Handle resource read requests"""
    return f"Resource content for {uri}"

@server.list_tools()
async def handle_list_tools() -> list[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_stock_info",
            description="Get basic information about a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, GOOGL, TSLA)"
                    }
                },
                "required": ["symbol"]
            },
        ),
        Tool(
            name="get_historical_data",
            description="Get historical stock price data",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period (1d, 5d, 1mo, 3mo, 6mo, 1y, 2y, 5y, 10y, ytd, max)",
                        "default": "1y"
                    },
                    "interval": {
                        "type": "string",
                        "description": "Data interval (1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo)",
                        "default": "1d"
                    }
                },
                "required": ["symbol"]
            },
        ),
        Tool(
            name="get_realtime_data",
            description="Get real-time stock price data",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    }
                },
                "required": ["symbol"]
            },
        ),
        Tool(
            name="calculate_technical_indicators",
            description="Calculate technical indicators for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period for calculation",
                        "default": "1y"
                    },
                    "indicators": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of indicators to calculate (sma_20, sma_50, sma_200, ema_12, ema_26, rsi, macd, bollinger_bands, stochastic, atr, volume_sma)"
                    }
                },
                "required": ["symbol"]
            },
        ),
        Tool(
            name="get_fundamental_data",
            description="Get fundamental financial data for a company",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    }
                },
                "required": ["symbol"]
            },
        ),
        Tool(
            name="get_company_news",
            description="Get latest news about a company",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Maximum number of news items to return",
                        "default": 10
                    }
                },
                "required": ["symbol"]
            },
        ),
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[types.TextContent | types.ImageContent | types.EmbeddedResource]:
    """Handle tool calls"""
    try:
        if name == "get_stock_info":
            symbol = arguments.get("symbol", "").upper()
            if not symbol:
                raise ValueError("Symbol is required")
            
            result = await finance_provider.get_stock_info(symbol)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_historical_data":
            symbol = arguments.get("symbol", "").upper()
            period = arguments.get("period", "1y")
            interval = arguments.get("interval", "1d")
            
            if not symbol:
                raise ValueError("Symbol is required")
            
            result = await finance_provider.get_historical_data(symbol, period, interval)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_realtime_data":
            symbol = arguments.get("symbol", "").upper()
            if not symbol:
                raise ValueError("Symbol is required")
            
            result = await finance_provider.get_realtime_data(symbol)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "calculate_technical_indicators":
            symbol = arguments.get("symbol", "").upper()
            period = arguments.get("period", "1y")
            indicators = arguments.get("indicators")
            
            if not symbol:
                raise ValueError("Symbol is required")
            
            result = await finance_provider.calculate_technical_indicators(symbol, period, indicators)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_fundamental_data":
            symbol = arguments.get("symbol", "").upper()
            if not symbol:
                raise ValueError("Symbol is required")
            
            result = await finance_provider.get_fundamental_data(symbol)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_company_news":
            symbol = arguments.get("symbol", "").upper()
            limit = arguments.get("limit", 10)
            
            if not symbol:
                raise ValueError("Symbol is required")
            
            result = await finance_provider.get_company_news(symbol, limit)
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        error_msg = f"Error executing {name}: {str(e)}"
        logger.error(error_msg)
        return [types.TextContent(type="text", text=json.dumps({"error": error_msg}))]

async def run_server():
    """Async function to run the MCP server"""
    from mcp.server.stdio import stdio_server
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="finance-mcp",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

def main():
    """Main entry point function - this is what gets called by the console script"""
    asyncio.run(run_server())

# Keep the old async main function for backwards compatibility but rename it
async def async_main():
    """Async main function (renamed from main to avoid conflicts)"""
    await run_server()

if __name__ == "__main__":
    main()