#!/usr/bin/env python3
"""
Optimized Finance MCP Server
Provides comprehensive stock market data and analysis through MCP protocol
Utilizes the complete yfinance API with optimizations and new features
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union, Tuple
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

class EnhancedFinanceDataProvider:
    """Enhanced class for handling financial data operations with full yfinance API utilization"""
    
    def __init__(self):
        self.cache = {}
        self.cache_duration = {
            'info': 300,  # 5 minutes for company info
            'realtime': 60,  # 1 minute for real-time data
            'news': 300,  # 5 minutes for news
            'fundamentals': 600,  # 10 minutes for fundamental data
            'options': 300,  # 5 minutes for options
            'institutional': 3600,  # 1 hour for institutional holdings
            'calendar': 3600,  # 1 hour for earnings calendar
            'recommendations': 1800,  # 30 minutes for analyst recommendations
            'upgrades_downgrades': 1800,  # 30 minutes for upgrades/downgrades
        }
        # Enable multi-threading for yfinance
        yf.enable_debug_mode()
    
    def _is_cache_valid(self, symbol: str, cache_type: str) -> bool:
        """Check if cached data is still valid"""
        cache_key = f"{symbol}_{cache_type}"
        if cache_key not in self.cache:
            return False
        
        cached_time = self.cache[cache_key].get('timestamp')
        if not cached_time:
            return False
            
        cache_duration = self.cache_duration.get(cache_type, 300)
        return (datetime.now() - cached_time).seconds < cache_duration
    
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
    
    def _safe_convert(self, value, convert_type=float, default='N/A'):
        """Safely convert values with fallback"""
        try:
            if pd.isna(value) or value is None:
                return default
            return convert_type(value)
        except (ValueError, TypeError):
            return default
    
    def _format_dataframe_to_dict(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Convert DataFrame to serializable dictionary"""
        if df.empty:
            return {}
        
        # Convert timestamps to strings and handle NaN values
        df_dict = {}
        for col in df.columns:
            df_dict[str(col)] = {}
            for idx in df.index:
                # Convert timestamps to string format
                key = str(idx) if not hasattr(idx, 'strftime') else idx.strftime('%Y-%m-%d')
                value = df.loc[idx, col]
                
                # Handle different data types
                if pd.isna(value):
                    df_dict[str(col)][key] = None
                elif isinstance(value, (int, float)):
                    df_dict[str(col)][key] = float(value) if not pd.isna(value) else None
                else:
                    df_dict[str(col)][key] = str(value)
        
        return df_dict

    async def get_comprehensive_stock_info(self, symbol: str) -> Dict[str, Any]:
        """Get comprehensive stock information using optimized yfinance calls"""
        try:
            # Check cache first
            cached_data = self._get_cached_data(symbol, 'info')
            if cached_data:
                return cached_data
            
            ticker = yf.Ticker(symbol)
            
            # Get all info in one call for efficiency
            info = ticker.info
            
            # Comprehensive stock information
            stock_info = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'basic_info': {
                    'company_name': info.get('longName', 'N/A'),
                    'short_name': info.get('shortName', 'N/A'),
                    'sector': info.get('sector', 'N/A'),
                    'industry': info.get('industry', 'N/A'),
                    'website': info.get('website', 'N/A'),
                    'business_summary': info.get('longBusinessSummary', 'N/A'),
                    'employees': info.get('fullTimeEmployees', 'N/A'),
                    'city': info.get('city', 'N/A'),
                    'state': info.get('state', 'N/A'),
                    'country': info.get('country', 'N/A'),
                    'phone': info.get('phone', 'N/A'),
                },
                'market_data': {
                    'market_cap': info.get('marketCap', 'N/A'),
                    'enterprise_value': info.get('enterpriseValue', 'N/A'),
                    'current_price': info.get('currentPrice', info.get('regularMarketPrice', 'N/A')),
                    'previous_close': info.get('previousClose', info.get('regularMarketPreviousClose', 'N/A')),
                    'open': info.get('open', info.get('regularMarketOpen', 'N/A')),
                    'day_high': info.get('dayHigh', info.get('regularMarketDayHigh', 'N/A')),
                    'day_low': info.get('dayLow', info.get('regularMarketDayLow', 'N/A')),
                    'volume': info.get('volume', info.get('regularMarketVolume', 'N/A')),
                    'avg_volume': info.get('averageVolume', 'N/A'),
                    'avg_volume_10days': info.get('averageVolume10days', 'N/A'),
                    '52_week_high': info.get('fiftyTwoWeekHigh', 'N/A'),
                    '52_week_low': info.get('fiftyTwoWeekLow', 'N/A'),
                    'fifty_day_average': info.get('fiftyDayAverage', 'N/A'),
                    'two_hundred_day_average': info.get('twoHundredDayAverage', 'N/A'),
                    'beta': info.get('beta', 'N/A'),
                    'shares_outstanding': info.get('sharesOutstanding', 'N/A'),
                    'float_shares': info.get('floatShares', 'N/A'),
                    'shares_short': info.get('sharesShort', 'N/A'),
                    'short_ratio': info.get('shortRatio', 'N/A'),
                    'short_percent_of_float': info.get('shortPercentOfFloat', 'N/A'),
                },
                'financial_metrics': {
                    'trailing_pe': info.get('trailingPE', 'N/A'),
                    'forward_pe': info.get('forwardPE', 'N/A'),
                    'peg_ratio': info.get('pegRatio', 'N/A'),
                    'price_to_book': info.get('priceToBook', 'N/A'),
                    'price_to_sales': info.get('priceToSalesTrailing12Months', 'N/A'),
                    'enterprise_to_revenue': info.get('enterpriseToRevenue', 'N/A'),
                    'enterprise_to_ebitda': info.get('enterpriseToEbitda', 'N/A'),
                    'profit_margins': info.get('profitMargins', 'N/A'),
                    'operating_margins': info.get('operatingMargins', 'N/A'),
                    'return_on_equity': info.get('returnOnEquity', 'N/A'),
                    'return_on_assets': info.get('returnOnAssets', 'N/A'),
                    'debt_to_equity': info.get('debtToEquity', 'N/A'),
                    'current_ratio': info.get('currentRatio', 'N/A'),
                    'quick_ratio': info.get('quickRatio', 'N/A'),
                },
                'dividend_info': {
                    'dividend_yield': info.get('dividendYield', 'N/A'),
                    'dividend_rate': info.get('dividendRate', 'N/A'),
                    'ex_dividend_date': info.get('exDividendDate', 'N/A'),
                    'payout_ratio': info.get('payoutRatio', 'N/A'),
                    'five_year_avg_dividend_yield': info.get('fiveYearAvgDividendYield', 'N/A'),
                },
                'revenue_earnings': {
                    'total_revenue': info.get('totalRevenue', 'N/A'),
                    'revenue_per_share': info.get('revenuePerShare', 'N/A'),
                    'revenue_growth': info.get('revenueGrowth', 'N/A'),
                    'quarterly_revenue_growth': info.get('quarterlyRevenueGrowth', 'N/A'),
                    'gross_profits': info.get('grossProfits', 'N/A'),
                    'ebitda': info.get('ebitda', 'N/A'),
                    'net_income': info.get('netIncomeToCommon', 'N/A'),
                    'trailing_eps': info.get('trailingEps', 'N/A'),
                    'forward_eps': info.get('forwardEps', 'N/A'),
                    'earnings_growth': info.get('earningsGrowth', 'N/A'),
                    'quarterly_earnings_growth': info.get('earningsQuarterlyGrowth', 'N/A'),
                },
                'cash_flow': {
                    'total_cash': info.get('totalCash', 'N/A'),
                    'total_cash_per_share': info.get('totalCashPerShare', 'N/A'),
                    'total_debt': info.get('totalDebt', 'N/A'),
                    'free_cashflow': info.get('freeCashflow', 'N/A'),
                    'operating_cashflow': info.get('operatingCashflow', 'N/A'),
                },
                'analyst_info': {
                    'recommendation_key': info.get('recommendationKey', 'N/A'),
                    'recommendation_mean': info.get('recommendationMean', 'N/A'),
                    'number_of_analyst_opinions': info.get('numberOfAnalystOpinions', 'N/A'),
                    'target_high_price': info.get('targetHighPrice', 'N/A'),
                    'target_low_price': info.get('targetLowPrice', 'N/A'),
                    'target_mean_price': info.get('targetMeanPrice', 'N/A'),
                    'target_median_price': info.get('targetMedianPrice', 'N/A'),
                }
            }
            
            # Cache the data
            self._set_cache_data(symbol, 'info', stock_info)
            return stock_info
            
        except Exception as e:
            logger.error(f"Error getting comprehensive stock info for {symbol}: {str(e)}")
            raise Exception(f"Failed to get comprehensive stock info: {str(e)}")

    async def get_historical_data(self, symbol: str, period: str = "1y", interval: str = "1d") -> Dict[str, Any]:
        """Get historical stock data with enhanced options"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Use optimized history call with additional parameters
            hist = ticker.history(
                period=period, 
                interval=interval,
                auto_adjust=True,  # Automatically adjust for splits and dividends
                back_adjust=True,  # Back-adjust prices for splits
                repair=True,  # Repair bad data
                keepna=False,  # Remove NaN values
                actions=True  # Include dividend and split actions
            )
            
            if hist.empty:
                raise Exception(f"No historical data found for {symbol}")
            
            # Convert to dictionary format with enhanced data
            historical_data = {
                'symbol': symbol,
                'period': period,
                'interval': interval,
                'timezone': str(hist.index.tz) if hasattr(hist.index, 'tz') else 'UTC',
                'data': [],
                'summary': {
                    'total_records': len(hist),
                    'start_date': hist.index[0].strftime('%Y-%m-%d') if len(hist) > 0 else None,
                    'end_date': hist.index[-1].strftime('%Y-%m-%d') if len(hist) > 0 else None,
                    'price_range': {
                        'highest': float(hist['High'].max()),
                        'lowest': float(hist['Low'].min()),
                        'avg_volume': int(hist['Volume'].mean()) if 'Volume' in hist.columns else 0
                    }
                }
            }
            
            for date, row in hist.iterrows():
                record = {
                    'date': date.strftime('%Y-%m-%d'),
                    'datetime': date.isoformat(),
                    'open': self._safe_convert(row['Open']),
                    'high': self._safe_convert(row['High']),
                    'low': self._safe_convert(row['Low']),
                    'close': self._safe_convert(row['Close']),
                    'volume': self._safe_convert(row['Volume'], int, 0)
                }
                
                # Add dividend and split information if available
                if 'Dividends' in row and not pd.isna(row['Dividends']) and row['Dividends'] > 0:
                    record['dividend'] = self._safe_convert(row['Dividends'])
                
                if 'Stock Splits' in row and not pd.isna(row['Stock Splits']) and row['Stock Splits'] != 1:
                    record['stock_split'] = self._safe_convert(row['Stock Splits'])
                
                historical_data['data'].append(record)
            
            return historical_data
            
        except Exception as e:
            logger.error(f"Error getting historical data for {symbol}: {str(e)}")
            raise Exception(f"Failed to get historical data: {str(e)}")

    async def get_options_data(self, symbol: str, expiration_date: Optional[str] = None) -> Dict[str, Any]:
        """Get options data for a stock"""
        try:
            # Check cache first
            cache_key = f"{expiration_date or 'all'}"
            cached_data = self._get_cached_data(symbol, f'options_{cache_key}')
            if cached_data:
                return cached_data
            
            ticker = yf.Ticker(symbol)
            
            # Get available expiration dates
            options_dates = ticker.options
            if not options_dates:
                return {
                    'symbol': symbol,
                    'message': 'No options data available',
                    'expiration_dates': [],
                    'options_chain': {}
                }
            
            options_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'expiration_dates': list(options_dates),
                'options_chain': {}
            }
            
            # If specific expiration date requested
            if expiration_date and expiration_date in options_dates:
                dates_to_process = [expiration_date]
            else:
                # Get data for all available dates (limit to first 5 for performance)
                dates_to_process = options_dates[:5]
            
            for exp_date in dates_to_process:
                try:
                    option_chain = ticker.option_chain(exp_date)
                    
                    # Process calls
                    calls_data = []
                    if not option_chain.calls.empty:
                        for _, call in option_chain.calls.iterrows():
                            calls_data.append({
                                'strike': self._safe_convert(call['strike']),
                                'last_price': self._safe_convert(call['lastPrice']),
                                'bid': self._safe_convert(call['bid']),
                                'ask': self._safe_convert(call['ask']),
                                'change': self._safe_convert(call['change']),
                                'percent_change': self._safe_convert(call['percentChange']),
                                'volume': self._safe_convert(call['volume'], int, 0),
                                'open_interest': self._safe_convert(call['openInterest'], int, 0),
                                'implied_volatility': self._safe_convert(call['impliedVolatility']),
                                'in_the_money': bool(call.get('inTheMoney', False)),
                                'contract_symbol': call.get('contractSymbol', 'N/A'),
                                'last_trade_date': call.get('lastTradeDate', 'N/A')
                            })
                    
                    # Process puts
                    puts_data = []
                    if not option_chain.puts.empty:
                        for _, put in option_chain.puts.iterrows():
                            puts_data.append({
                                'strike': self._safe_convert(put['strike']),
                                'last_price': self._safe_convert(put['lastPrice']),
                                'bid': self._safe_convert(put['bid']),
                                'ask': self._safe_convert(put['ask']),
                                'change': self._safe_convert(put['change']),
                                'percent_change': self._safe_convert(put['percentChange']),
                                'volume': self._safe_convert(put['volume'], int, 0),
                                'open_interest': self._safe_convert(put['openInterest'], int, 0),
                                'implied_volatility': self._safe_convert(put['impliedVolatility']),
                                'in_the_money': bool(put.get('inTheMoney', False)),
                                'contract_symbol': put.get('contractSymbol', 'N/A'),
                                'last_trade_date': put.get('lastTradeDate', 'N/A')
                            })
                    
                    options_data['options_chain'][exp_date] = {
                        'calls': calls_data,
                        'puts': puts_data,
                        'call_count': len(calls_data),
                        'put_count': len(puts_data)
                    }
                    
                except Exception as e:
                    logger.warning(f"Error processing options for {exp_date}: {str(e)}")
                    continue
            
            # Cache the data
            self._set_cache_data(symbol, f'options_{cache_key}', options_data)
            return options_data
            
        except Exception as e:
            logger.error(f"Error getting options data for {symbol}: {str(e)}")
            raise Exception(f"Failed to get options data: {str(e)}")

    async def get_institutional_holders(self, symbol: str) -> Dict[str, Any]:
        """Get institutional holders data"""
        try:
            # Check cache first
            cached_data = self._get_cached_data(symbol, 'institutional')
            if cached_data:
                return cached_data
            
            ticker = yf.Ticker(symbol)
            
            # Get institutional holders
            institutional_holders = ticker.institutional_holders
            major_holders = ticker.major_holders
            
            holders_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'institutional_holders': [],
                'major_holders': {}
            }
            
            # Process institutional holders
            if not institutional_holders.empty:
                for _, holder in institutional_holders.iterrows():
                    holders_data['institutional_holders'].append({
                        'holder': holder.get('Holder', 'N/A'),
                        'shares': self._safe_convert(holder.get('Shares'), int, 0),
                        'date_reported': str(holder.get('Date Reported', 'N/A')),
                        'percent_out': self._safe_convert(holder.get('% Out')),
                        'value': self._safe_convert(holder.get('Value'), int, 0)
                    })
            
            # Process major holders
            if not major_holders.empty:
                for idx, row in major_holders.iterrows():
                    if len(row) >= 2:
                        holders_data['major_holders'][str(row.iloc[1])] = str(row.iloc[0])
            
            # Cache the data
            self._set_cache_data(symbol, 'institutional', holders_data)
            return holders_data
            
        except Exception as e:
            logger.error(f"Error getting institutional holders for {symbol}: {str(e)}")
            raise Exception(f"Failed to get institutional holders: {str(e)}")

    async def get_earnings_calendar(self, symbol: str) -> Dict[str, Any]:
        """Get earnings calendar and estimates"""
        try:
            # Check cache first
            cached_data = self._get_cached_data(symbol, 'calendar')
            if cached_data:
                return cached_data
            
            ticker = yf.Ticker(symbol)
            
            # Get calendar and earnings data
            calendar_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'earnings_calendar': {},
                'earnings_history': [],
                'analyst_price_targets': {}
            }
            
            # Get earnings calendar
            try:
                calendar = ticker.calendar
                if not calendar.empty:
                    calendar_data['earnings_calendar'] = self._format_dataframe_to_dict(calendar)
            except Exception as e:
                logger.warning(f"Could not fetch calendar for {symbol}: {str(e)}")
            
            # Get earnings history
            try:
                earnings = ticker.earnings
                if not earnings.empty:
                    for date, row in earnings.iterrows():
                        calendar_data['earnings_history'].append({
                            'year': str(date),
                            'revenue': self._safe_convert(row.get('Revenue')),
                            'earnings': self._safe_convert(row.get('Earnings'))
                        })
            except Exception as e:
                logger.warning(f"Could not fetch earnings history for {symbol}: {str(e)}")
            
            # Get analyst price targets
            try:
                targets = ticker.analyst_price_targets
                if targets:
                    calendar_data['analyst_price_targets'] = {
                        'current': self._safe_convert(targets.get('current')),
                        'high': self._safe_convert(targets.get('high')),
                        'low': self._safe_convert(targets.get('low')),
                        'mean': self._safe_convert(targets.get('mean')),
                        'median': self._safe_convert(targets.get('median'))
                    }
            except Exception as e:
                logger.warning(f"Could not fetch analyst targets for {symbol}: {str(e)}")
            
            # Cache the data
            self._set_cache_data(symbol, 'calendar', calendar_data)
            return calendar_data
            
        except Exception as e:
            logger.error(f"Error getting earnings calendar for {symbol}: {str(e)}")
            raise Exception(f"Failed to get earnings calendar: {str(e)}")

    async def get_analyst_recommendations(self, symbol: str) -> Dict[str, Any]:
        """Get analyst recommendations and upgrades/downgrades"""
        try:
            # Check cache first
            cached_data = self._get_cached_data(symbol, 'recommendations')
            if cached_data:
                return cached_data
            
            ticker = yf.Ticker(symbol)
            
            recommendations_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'recommendations': [],
                'upgrades_downgrades': []
            }
            
            # Get recommendations
            try:
                recommendations = ticker.recommendations
                if not recommendations.empty:
                    for date, row in recommendations.iterrows():
                        recommendations_data['recommendations'].append({
                            'date': date.strftime('%Y-%m-%d'),
                            'firm': row.get('Firm', 'N/A'),
                            'to_grade': row.get('To Grade', 'N/A'),
                            'from_grade': row.get('From Grade', 'N/A'),
                            'action': row.get('Action', 'N/A')
                        })
            except Exception as e:
                logger.warning(f"Could not fetch recommendations for {symbol}: {str(e)}")
            
            # Get upgrades/downgrades
            try:
                upgrades_downgrades = ticker.upgrades_downgrades
                if not upgrades_downgrades.empty:
                    for date, row in upgrades_downgrades.iterrows():
                        recommendations_data['upgrades_downgrades'].append({
                            'date': date.strftime('%Y-%m-%d'),
                            'firm': row.get('Firm', 'N/A'),
                            'to_grade': row.get('ToGrade', 'N/A'),
                            'from_grade': row.get('FromGrade', 'N/A'),
                            'action': row.get('Action', 'N/A')
                        })
            except Exception as e:
                logger.warning(f"Could not fetch upgrades/downgrades for {symbol}: {str(e)}")
            
            # Cache the data
            self._set_cache_data(symbol, 'recommendations', recommendations_data)
            return recommendations_data
            
        except Exception as e:
            logger.error(f"Error getting analyst recommendations for {symbol}: {str(e)}")
            raise Exception(f"Failed to get analyst recommendations: {str(e)}")

    async def get_financial_statements(self, symbol: str, statement_type: str = "all") -> Dict[str, Any]:
        """Get comprehensive financial statements"""
        try:
            ticker = yf.Ticker(symbol)
            
            statements_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'income_statement': {},
                'balance_sheet': {},
                'cash_flow': {},
                'quarterly_income_statement': {},
                'quarterly_balance_sheet': {},
                'quarterly_cash_flow': {}
            }
            
            # Get annual statements
            if statement_type in ["all", "income"]:
                try:
                    income_stmt = ticker.income_stmt
                    if not income_stmt.empty:
                        statements_data['income_statement'] = self._format_dataframe_to_dict(income_stmt)
                except Exception as e:
                    logger.warning(f"Could not fetch income statement for {symbol}: {str(e)}")
            
            if statement_type in ["all", "balance"]:
                try:
                    balance_sheet = ticker.balance_sheet
                    if not balance_sheet.empty:
                        statements_data['balance_sheet'] = self._format_dataframe_to_dict(balance_sheet)
                except Exception as e:
                    logger.warning(f"Could not fetch balance sheet for {symbol}: {str(e)}")
            
            if statement_type in ["all", "cashflow"]:
                try:
                    cash_flow = ticker.cashflow
                    if not cash_flow.empty:
                        statements_data['cash_flow'] = self._format_dataframe_to_dict(cash_flow)
                except Exception as e:
                    logger.warning(f"Could not fetch cash flow for {symbol}: {str(e)}")
            
            # Get quarterly statements
            if statement_type in ["all", "quarterly_income"]:
                try:
                    quarterly_income = ticker.quarterly_income_stmt
                    if not quarterly_income.empty:
                        statements_data['quarterly_income_statement'] = self._format_dataframe_to_dict(quarterly_income)
                except Exception as e:
                    logger.warning(f"Could not fetch quarterly income statement for {symbol}: {str(e)}")
            
            if statement_type in ["all", "quarterly_balance"]:
                try:
                    quarterly_balance = ticker.quarterly_balance_sheet
                    if not quarterly_balance.empty:
                        statements_data['quarterly_balance_sheet'] = self._format_dataframe_to_dict(quarterly_balance)
                except Exception as e:
                    logger.warning(f"Could not fetch quarterly balance sheet for {symbol}: {str(e)}")
            
            if statement_type in ["all", "quarterly_cashflow"]:
                try:
                    quarterly_cashflow = ticker.quarterly_cashflow
                    if not quarterly_cashflow.empty:
                        statements_data['quarterly_cash_flow'] = self._format_dataframe_to_dict(quarterly_cashflow)
                except Exception as e:
                    logger.warning(f"Could not fetch quarterly cash flow for {symbol}: {str(e)}")
            
            return statements_data
            
        except Exception as e:
            logger.error(f"Error getting financial statements for {symbol}: {str(e)}")
            raise Exception(f"Failed to get financial statements: {str(e)}")

    async def get_news(self, symbol: str, limit: int = 10) -> Dict[str, Any]:
        """Get latest news for a stock"""
        try:
            # Check cache first
            cached_data = self._get_cached_data(symbol, 'news')
            if cached_data:
                return cached_data
            
            ticker = yf.Ticker(symbol)
            
            # Get news
            news = ticker.news
            
            news_data = {
                'symbol': symbol,
                'timestamp': datetime.now().isoformat(),
                'news_count': len(news),
                'news': []
            }
            
            for article in news[:limit]:
                news_item = {
                    'title': article.get('title', 'N/A'),
                    'publisher': article.get('publisher', 'N/A'),
                    'link': article.get('link', 'N/A'),
                    'provider_publish_time': article.get('providerPublishTime', 'N/A'),
                    'type': article.get('type', 'N/A'),
                    'thumbnail': article.get('thumbnail', {}).get('resolutions', [{}])[0].get('url', 'N/A') if article.get('thumbnail') else 'N/A',
                    'related_tickers': article.get('relatedTickers', [])
                }
                news_data['news'].append(news_item)
            
            # Cache the data
            self._set_cache_data(symbol, 'news', news_data)
            return news_data
            
        except Exception as e:
            logger.error(f"Error getting news for {symbol}: {str(e)}")
            raise Exception(f"Failed to get news: {str(e)}")

    async def get_technical_analysis(self, symbol: str, period: str = "1y") -> Dict[str, Any]:
        """Get technical analysis indicators"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get historical data for technical analysis
            hist = ticker.history(period=period, interval="1d")
            
            if hist.empty:
                raise Exception(f"No data available for technical analysis of {symbol}")
            
            # Calculate technical indicators using ta library
            analysis_data = {
                'symbol': symbol,
                'period': period,
                'timestamp': datetime.now().isoformat(),
                'indicators': {}
            }
            
            # Moving Averages
            analysis_data['indicators']['moving_averages'] = {
                'sma_20': float(ta.trend.sma_indicator(hist['Close'], window=20).iloc[-1]) if len(hist) >= 20 else None,
                'sma_50': float(ta.trend.sma_indicator(hist['Close'], window=50).iloc[-1]) if len(hist) >= 50 else None,
                'sma_200': float(ta.trend.sma_indicator(hist['Close'], window=200).iloc[-1]) if len(hist) >= 200 else None,
                'ema_12': float(ta.trend.ema_indicator(hist['Close'], window=12).iloc[-1]) if len(hist) >= 12 else None,
                'ema_26': float(ta.trend.ema_indicator(hist['Close'], window=26).iloc[-1]) if len(hist) >= 26 else None,
            }
            
            # RSI
            rsi = ta.momentum.rsi(hist['Close'], window=14)
            analysis_data['indicators']['rsi'] = {
                'current': float(rsi.iloc[-1]) if not rsi.empty else None,
                'signal': 'oversold' if not rsi.empty and rsi.iloc[-1] < 30 else 'overbought' if not rsi.empty and rsi.iloc[-1] > 70 else 'neutral'
            }
            
            # MACD
            macd_line = ta.trend.macd(hist['Close'])
            macd_signal = ta.trend.macd_signal(hist['Close'])
            macd_histogram = ta.trend.macd_diff(hist['Close'])
            
            analysis_data['indicators']['macd'] = {
                'macd_line': float(macd_line.iloc[-1]) if not macd_line.empty else None,
                'signal_line': float(macd_signal.iloc[-1]) if not macd_signal.empty else None,
                'histogram': float(macd_histogram.iloc[-1]) if not macd_histogram.empty else None,
                'signal': 'bullish' if not macd_histogram.empty and macd_histogram.iloc[-1] > 0 else 'bearish'
            }
            
            # Bollinger Bands
            bb_high = ta.volatility.bollinger_hband(hist['Close'])
            bb_low = ta.volatility.bollinger_lband(hist['Close'])
            bb_mid = ta.volatility.bollinger_mavg(hist['Close'])
            
            current_price = float(hist['Close'].iloc[-1])
            analysis_data['indicators']['bollinger_bands'] = {
                'upper_band': float(bb_high.iloc[-1]) if not bb_high.empty else None,
                'middle_band': float(bb_mid.iloc[-1]) if not bb_mid.empty else None,
                'lower_band': float(bb_low.iloc[-1]) if not bb_low.empty else None,
                'position': 'above_upper' if not bb_high.empty and current_price > bb_high.iloc[-1] else 'below_lower' if not bb_low.empty and current_price < bb_low.iloc[-1] else 'middle'
            }
            
            # Volume indicators
            analysis_data['indicators']['volume'] = {
                'volume_sma_20': float(hist['Volume'].rolling(window=20).mean().iloc[-1]) if len(hist) >= 20 else None,
                'volume_ratio': float(hist['Volume'].iloc[-1] / hist['Volume'].rolling(20).mean().iloc[-1]) if len(hist) >= 20 else None
            }
            
            # Support and Resistance (simple calculation)
            recent_data = hist.tail(50)  # Last 50 days
            analysis_data['indicators']['support_resistance'] = {
                'support_level': float(recent_data['Low'].min()),
                'resistance_level': float(recent_data['High'].max()),
                'current_price': current_price
            }
            
            return analysis_data
            
        except Exception as e:
            logger.error(f"Error getting technical analysis for {symbol}: {str(e)}")
            raise Exception(f"Failed to get technical analysis: {str(e)}")

    async def get_sector_performance(self, symbols: List[str]) -> Dict[str, Any]:
        """Get performance comparison for multiple symbols"""
        try:
            performance_data = {
                'timestamp': datetime.now().isoformat(),
                'symbols': symbols,
                'performance': {}
            }
            
            for symbol in symbols:
                try:
                    ticker = yf.Ticker(symbol)
                    hist = ticker.history(period="1y", interval="1d")
                    info = ticker.info
                    
                    if not hist.empty:
                        # Calculate performance metrics
                        start_price = float(hist['Close'].iloc[0])
                        current_price = float(hist['Close'].iloc[-1])
                        ytd_return = ((current_price - start_price) / start_price) * 100
                        
                        # Calculate volatility (standard deviation of daily returns)
                        daily_returns = hist['Close'].pct_change().dropna()
                        volatility = float(daily_returns.std() * (252 ** 0.5) * 100)  # Annualized volatility
                        
                        performance_data['performance'][symbol] = {
                            'company_name': info.get('longName', symbol),
                            'sector': info.get('sector', 'N/A'),
                            'current_price': current_price,
                            'ytd_return_percent': round(ytd_return, 2),
                            'volatility_percent': round(volatility, 2),
                            'market_cap': info.get('marketCap', 'N/A'),
                            'pe_ratio': info.get('trailingPE', 'N/A'),
                            'beta': info.get('beta', 'N/A')
                        }
                    
                except Exception as e:
                    logger.warning(f"Error processing {symbol}: {str(e)}")
                    performance_data['performance'][symbol] = {
                        'error': f"Failed to get data: {str(e)}"
                    }
            
            return performance_data
            
        except Exception as e:
            logger.error(f"Error getting sector performance: {str(e)}")
            raise Exception(f"Failed to get sector performance: {str(e)}")

    async def get_dividend_history(self, symbol: str, period: str = "2y") -> Dict[str, Any]:
        """Get dividend history for a stock"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get dividend data
            dividends = ticker.dividends
            
            dividend_data = {
                'symbol': symbol,
                'period': period,
                'timestamp': datetime.now().isoformat(),
                'dividend_history': [],
                'summary': {
                    'total_dividends': 0,
                    'dividend_count': 0,
                    'avg_dividend': 0,
                    'last_dividend': 0,
                    'last_dividend_date': None
                }
            }
            
            if not dividends.empty:
                # Filter by period
                end_date = datetime.now()
                if period == "1y":
                    start_date = end_date - timedelta(days=365)
                elif period == "2y":
                    start_date = end_date - timedelta(days=730)
                elif period == "5y":
                    start_date = end_date - timedelta(days=1825)
                else:
                    start_date = dividends.index[0]
                
                filtered_dividends = dividends[dividends.index >= start_date]
                
                for date, dividend in filtered_dividends.items():
                    dividend_data['dividend_history'].append({
                        'date': date.strftime('%Y-%m-%d'),
                        'dividend': float(dividend)
                    })
                
                # Calculate summary
                dividend_data['summary'] = {
                    'total_dividends': float(filtered_dividends.sum()),
                    'dividend_count': len(filtered_dividends),
                    'avg_dividend': float(filtered_dividends.mean()) if len(filtered_dividends) > 0 else 0,
                    'last_dividend': float(filtered_dividends.iloc[-1]) if len(filtered_dividends) > 0 else 0,
                    'last_dividend_date': filtered_dividends.index[-1].strftime('%Y-%m-%d') if len(filtered_dividends) > 0 else None
                }
            
            return dividend_data
            
        except Exception as e:
            logger.error(f"Error getting dividend history for {symbol}: {str(e)}")
            raise Exception(f"Failed to get dividend history: {str(e)}")

# Initialize the data provider
finance_provider = EnhancedFinanceDataProvider()

# Define MCP Tools
@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools"""
    return [
        Tool(
            name="get_comprehensive_stock_info",
            description="Get comprehensive stock information including company details, market data, financial metrics, and analyst information",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol (e.g., AAPL, GOOGL, TSLA)"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_historical_data",
            description="Get historical stock price data with customizable period and interval",
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
            }
        ),
        Tool(
            name="get_options_data",
            description="Get options chain data for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "expiration_date": {
                        "type": "string",
                        "description": "Specific expiration date (YYYY-MM-DD format), or leave empty for all available dates"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_institutional_holders",
            description="Get institutional holders and major shareholders data",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_earnings_calendar",
            description="Get earnings calendar, history, and analyst price targets",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_analyst_recommendations",
            description="Get analyst recommendations, upgrades, and downgrades",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_financial_statements",
            description="Get comprehensive financial statements (income statement, balance sheet, cash flow)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "statement_type": {
                        "type": "string",
                        "description": "Type of statement: 'all', 'income', 'balance', 'cashflow', 'quarterly_income', 'quarterly_balance', 'quarterly_cashflow'",
                        "default": "all"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_news",
            description="Get latest news for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "limit": {
                        "type": "integer",
                        "description": "Number of news articles to return",
                        "default": 10
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_technical_analysis",
            description="Get technical analysis indicators including moving averages, RSI, MACD, Bollinger Bands",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period for analysis",
                        "default": "1y"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_sector_performance",
            description="Compare performance of multiple stocks",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbols": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of stock symbols to compare"
                    }
                },
                "required": ["symbols"]
            }
        ),
        Tool(
            name="get_dividend_history",
            description="Get dividend payment history for a stock",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Stock symbol"
                    },
                    "period": {
                        "type": "string",
                        "description": "Time period (1y, 2y, 5y, max)",
                        "default": "2y"
                    }
                },
                "required": ["symbol"]
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[types.TextContent]:
    """Handle tool calls"""
    try:
        if name == "get_comprehensive_stock_info":
            result = await finance_provider.get_comprehensive_stock_info(arguments["symbol"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_historical_data":
            result = await finance_provider.get_historical_data(
                arguments["symbol"],
                arguments.get("period", "1y"),
                arguments.get("interval", "1d")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_options_data":
            result = await finance_provider.get_options_data(
                arguments["symbol"],
                arguments.get("expiration_date")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_institutional_holders":
            result = await finance_provider.get_institutional_holders(arguments["symbol"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_earnings_calendar":
            result = await finance_provider.get_earnings_calendar(arguments["symbol"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_analyst_recommendations":
            result = await finance_provider.get_analyst_recommendations(arguments["symbol"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_financial_statements":
            result = await finance_provider.get_financial_statements(
                arguments["symbol"],
                arguments.get("statement_type", "all")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_news":
            result = await finance_provider.get_news(
                arguments["symbol"],
                arguments.get("limit", 10)
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_technical_analysis":
            result = await finance_provider.get_technical_analysis(
                arguments["symbol"],
                arguments.get("period", "1y")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_sector_performance":
            result = await finance_provider.get_sector_performance(arguments["symbols"])
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        elif name == "get_dividend_history":
            result = await finance_provider.get_dividend_history(
                arguments["symbol"],
                arguments.get("period", "2y")
            )
            return [types.TextContent(type="text", text=json.dumps(result, indent=2))]
        
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    except Exception as e:
        logger.error(f"Error in tool {name}: {str(e)}")
        return [types.TextContent(type="text", text=f"Error: {str(e)}")]

@server.list_resources()
async def handle_list_resources() -> List[Resource]:
    """List available resources"""
    return [
        Resource(
            uri="finance://market-overview",
            name="Market Overview",
            description="Get general market overview and trending stocks",
            mimeType="application/json"
        ),
        Resource(
            uri="finance://sectors",
            name="Sector Information",
            description="Information about different market sectors",
            mimeType="application/json"
        )
    ]

@server.read_resource()
async def handle_read_resource(uri: str) -> str:
    """Handle resource reading"""
    try:
        if uri == "finance://market-overview":
            # Get data for major indices
            major_indices = ["^GSPC", "^DJI", "^IXIC", "^RUT"]  # S&P 500, Dow Jones, NASDAQ, Russell 2000
            overview_data = await finance_provider.get_sector_performance(major_indices)
            return json.dumps(overview_data, indent=2)
        
        elif uri == "finance://sectors":
            # Example sector ETFs
            sector_etfs = ["XLK", "XLF", "XLE", "XLV", "XLI", "XLP", "XLY", "XLU", "XLRE", "XLB", "XLC"]
            sector_data = await finance_provider.get_sector_performance(sector_etfs)
            return json.dumps(sector_data, indent=2)
        
        else:
            raise ValueError(f"Unknown resource: {uri}")
    
    except Exception as e:
        logger.error(f"Error reading resource {uri}: {str(e)}")
        return json.dumps({"error": str(e)})

async def main():
    """Main function to run the MCP server"""
    # Import here to avoid issues with asyncio
    from mcp.server.stdio import stdio_server
    
    logger.info("Starting Enhanced Finance MCP Server...")
    
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="enhanced-finance-mcp",
                server_version="2.0.0",
                capabilities=server.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={}
                )
            )
        )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {str(e)}")
        raise