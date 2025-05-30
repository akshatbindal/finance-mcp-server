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

## [Unreleased]

### Planned Features
- Additional technical indicators
- Cryptocurrency support
- Options data
- News sentiment analysis
- Portfolio tracking
- Custom indicator calculations