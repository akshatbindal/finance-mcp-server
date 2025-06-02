# 📈 Finance MCP Server

[![PyPI version](https://badge.fury.io/py/finance-mcp-server.svg)](https://badge.fury.io/py/finance-mcp-server)
[![Python Support](https://img.shields.io/pypi/pyversions/finance-mcp-server.svg)](https://pypi.org/project/finance-mcp-server/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Model Context Protocol (MCP) server that brings comprehensive stock market data and technical analysis capabilities to Claude Desktop and other MCP-compatible clients.

## 🚀 Features

- **📊 Stock Information**: Complete company profiles, market metrics, and key statistics
- **📈 Historical Data**: Customizable historical price data with multiple timeframes
- **⚡ Real-time Quotes**: Live stock prices with change calculations
- **🔧 Technical Indicators**: 10+ professional-grade technical analysis tools
- **🚀 High Performance**: Intelligent caching system for optimal speed
- **🛡️ Robust**: Comprehensive error handling and validation
- **🔌 Easy Integration**: One-command installation for Claude Desktop

## 📦 Quick Installation

### For Claude Desktop Users

```bash
pip install finance-mcp-server
```

Then add to your Claude Desktop configuration:

```json
{
  "mcpServers": {
    "finance": {
      "command": "finance-mcp-server"
    }
  }
}
```

Restart Claude Desktop and start asking about stocks! 🎉

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/akshatbindal/finance-mcp-server.git
cd finance-mcp-server

# Install in development mode
pip install -e .

# Or install from PyPI
pip install finance-mcp-server
```

## 🎯 Usage Examples

Once installed, you can ask Claude Desktop natural language questions like:

- *"What's Apple's current stock price and market cap?"*
- *"Show me Tesla's performance over the last 6 months"*
- *"Calculate RSI and MACD for Microsoft stock"*
- *"Compare the 50-day moving average of Google vs Amazon"*
- *"What are the Bollinger Bands for Netflix right now?"*

## 🛠️ Available Tools

The Finance MCP Server exposes the following tools via the MCP protocol:

- **get_comprehensive_stock_info**: Get detailed company, market, financial, and analyst data for any stock symbol.
- **get_historical_data**: Retrieve historical price data with customizable period and interval, including splits/dividends.
- **get_options_data**: Fetch options chain data for a stock, including calls and puts for multiple expiration dates.
- **get_institutional_holders**: View institutional and major holders for a stock.
- **get_earnings_calendar**: Access earnings calendar, history, and analyst price targets.
- **get_analyst_recommendations**: Analyst recommendations, upgrades, and downgrades.
- **get_financial_statements**: Download full income statement, balance sheet, and cash flow (annual/quarterly).
- **get_news**: Latest news headlines and metadata for a stock.
- **get_technical_analysis**: Professional indicators (SMA, EMA, RSI, MACD, Bollinger Bands, volume, support/resistance, etc).
- **get_sector_performance**: Compare performance, volatility, and metrics for multiple stocks.
- **get_dividend_history**: Dividend payment history, summary, and stats.

### Example Tool Call (MCP JSON)
```json
{
  "tool": "get_comprehensive_stock_info",
  "arguments": {"symbol": "AAPL"}
}
```

### Caching & Performance
- **Company info, news, options, holders, calendar, recommendations**: 5–60 min cache
- **Real-time data**: 1 min cache
- **Fundamentals**: 10 min cache
- **Optimized yfinance usage**: Multi-threading enabled, batch requests, and error isolation

### Error Handling
- All endpoints return clear error messages on failure
- Graceful fallback for missing or partial data
- Logging for all exceptions and warnings

### Technical Analysis
- Moving averages (SMA 20/50/200, EMA 12/26)
- RSI, MACD, Bollinger Bands, volume trends
- Support/resistance, volatility, and more

### Expanded Data
- Options chain (calls/puts, OI, IV, last trade)
- Institutional/major holders
- Earnings calendar/history, analyst targets
- Full financial statements (annual/quarterly)
- News headlines, publisher, related tickers
- Dividend history and summary

## 🛠️ Configuration

### Basic Configuration
```json
{
  "mcpServers": {
    "finance": {
      "command": "finance-mcp-server"
    }
  }
}
```

### Advanced Configuration
```json
{
  "mcpServers": {
    "finance": {
      "command": "finance-mcp-server",
      "env": {
        "LOG_LEVEL": "INFO",
        "CACHE_DURATION": "300"
      }
    }
  }
}
```

## 🔧 Development

### Setting Up Development Environment

```bash
# Clone the repository
git clone https://github.com/akshatbindal/finance-mcp-server.git
cd finance-mcp-server

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8 mypy

# Run tests
pytest

# Format code
black finance_mcp/

# Type checking
mypy finance_mcp/
```

### Running the Server

```bash
# Run directly
python -m finance_mcp.server

# Or use the console script
finance-mcp-server

# With debug logging
LOG_LEVEL=DEBUG finance-mcp-server
```

## 📊 Performance Features

### Intelligent Caching
- **Stock Info & Technical Indicators**: 5-minute cache
- **Real-time Data**: 1-minute cache
- **Historical Data**: Session-based caching
- Automatic cache invalidation

### Error Handling
- Graceful handling of invalid stock symbols
- Network timeout protection
- Comprehensive error messages
- Fallback mechanisms for data retrieval

## 🔒 Privacy & Security

- **No Data Storage**: All data is retrieved in real-time from Yahoo Finance
- **No User Tracking**: No personal information is collected or stored
- **Rate Limiting**: Built-in protection against API abuse
- **Error Isolation**: Errors don't crash the entire server

## 🤝 Contributing

We welcome contributions! Here's how you can help:

1. **Fork the repository**
2. **Create a feature branch**: `git checkout -b feature/amazing-feature`
3. **Make your changes** and add tests
4. **Run the test suite**: `pytest`
5. **Format your code**: `black finance_mcp/`
6. **Submit a pull request**

### Areas for Contribution
- Additional technical indicators
- Cryptocurrency support
- Options and futures data
- News sentiment integration
- Performance optimizations
- Documentation improvements

## 📋 Requirements

- **Python**: 3.8 or higher
- **Dependencies**:
  - `mcp >= 1.0.0` - Model Context Protocol framework
  - `yfinance >= 0.2.18` - Yahoo Finance API wrapper
  - `pandas >= 2.0.0` - Data manipulation and analysis
  - `ta >= 0.10.2` - Technical analysis library

## 🐛 Troubleshooting

### Common Issues

**Server not starting?**
```bash
# Check if all dependencies are installed
pip install -r requirements.txt

# Test the server manually
finance-mcp-server
```

**No data for a symbol?**
- Verify the stock symbol is correct (e.g., "AAPL" not "Apple")
- Check if the market is open (affects real-time data)
- Some symbols may not be available on Yahoo Finance

**Claude Desktop not connecting?**
- Ensure the configuration JSON is valid
- Check that the command path is correct
- Restart Claude Desktop completely
- Check Claude Desktop's logs for error messages

### Getting Help

- **GitHub Issues**: [Report bugs or request features](https://github.com/akshatbindal/finance-mcp-server/issues)
- **Discussions**: [Community support and questions](https://github.com/akshatbindal/finance-mcp-server/discussions)
- **Documentation**: [Full documentation and examples](https://github.com/akshatbindal/finance-mcp-server/wiki)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Yahoo Finance** for providing free financial data
- **MCP Team** for the Model Context Protocol framework
- **Technical Analysis Library** contributors
- **Open Source Community** for inspiration and support

## 🔮 Roadmap

### Version 1.1.0 (Coming Soon)
- [ ] Cryptocurrency support (Bitcoin, Ethereum, etc.)
- [ ] Options chain data
- [ ] Earnings calendar integration
- [ ] News sentiment analysis

### Version 1.2.0 (Future)
- [ ] Portfolio tracking capabilities
- [ ] Custom indicator builder
- [ ] Multi-timeframe analysis
- [ ] Advanced charting data

### Version 2.0.0 (Vision)
- [ ] Machine learning predictions
- [ ] Risk analysis tools
- [ ] Backtesting framework
- [ ] Professional trader features

---

## ⭐ Star History

[![Star History Chart](https://api.star-history.com/svg?repos=akshatbindal/finance-mcp-server&type=Date)](https://star-history.com/#akshatbindal/finance-mcp-server&Date)

---

**Made with ❤️ for the MCP and trading communities**

*Bringing professional-grade financial analysis to conversational AI*