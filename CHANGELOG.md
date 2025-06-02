# CHANGELOG.md
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2024-01-XX

### Added
- Initial release of Finance MCP Server
- Stock information retrieval (company data, market metrics)
- Historical data access with customizable periods and intervals
- Real-time stock quotes with change calculations
- Technical indicators calculation:
  - Simple Moving Averages (SMA 20, 50, 200)
  - Exponential Moving Averages (EMA 12, 26)
  - Relative Strength Index (RSI)
  - MACD with signal line and histogram
  - Bollinger Bands (upper, lower, middle)
  - Stochastic Oscillator (%K and %D)
  - Average True Range (ATR)
  - Volume Simple Moving Average
- Intelligent caching system (5-minute for general data, 1-minute for real-time)
- Comprehensive error handling and logging
- MCP protocol compliance with resources and tools
- CLI entry point for easy installation

### Technical Details
- Built with yfinance for data retrieval
- Uses ta library for technical analysis
- Implements Model Context Protocol (MCP)
- Python 3.8+ support
- Async/await support for non-blocking operations

## [1.1.0] - 2025-06-02

### Added
- Major refactor and optimization of the Finance MCP Server backend
- Full yfinance API utilization for all endpoints
- New endpoints: options data, institutional holders, earnings calendar/history, analyst recommendations, financial statements, news, sector performance, dividend history
- Expanded technical analysis: support/resistance, volatility, volume ratios, and more
- Advanced caching system with per-endpoint durations (1 min to 1 hour)
- Multi-threading enabled for yfinance
- Improved error handling and logging for all endpoints
- Data formatting improvements for DataFrames and API responses
- Enhanced MCP tool schemas and documentation

### Changed
- All endpoints now return more detailed and structured data
- Optimized historical data retrieval (auto-adjust, back-adjust, repair, actions)
- Technical indicators now use the latest ta library features
- Improved summary and stats for dividend and sector performance endpoints

### Fixed
- Graceful fallback for missing or partial data
- Robust error isolation (one endpoint failure does not affect others)
- Minor bug fixes in data conversion and formatting

## [Unreleased]

### Planned Features
- Additional technical indicators
- Cryptocurrency support
- Options data
- News sentiment analysis
- Portfolio tracking
- Custom indicator calculations