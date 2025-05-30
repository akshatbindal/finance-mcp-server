# finance_mcp/__init__.py
"""
Finance MCP Server - Stock market data and technical analysis
"""

__version__ = "1.0.0"
__author__ = "Akshat Bindal"
__email__ = "akshatbindal01@gmail.com"
__description__ = "MCP Server for Financial Data and Technical Indicators"

from .server import main

__all__ = ["main"]

# setup.py
from setuptools import setup, find_packages
import os

# Read README file
def read_readme():
    with open("README.md", "r", encoding="utf-8") as fh:
        return fh.read()

# Read requirements
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as fh:
        return [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="finance-mcp-server",
    version="1.0.0",
    author="Akshat Bindal",
    author_email="akshatbindal01@gmail.com",
    description="MCP Server for Financial Data and Technical Indicators",
    long_description=read_readme(),
    long_description_content_type="text/markdown",
    url="https://github.com/akshatbindal/finance-mcp-server",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Office/Business :: Financial",
        "Topic :: Office/Business :: Financial :: Investment",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    python_requires=">=3.8",
    install_requires=read_requirements(),
    entry_points={
        "console_scripts": [
            "finance-mcp-server=finance_mcp.server:main",
        ],
    },
    keywords="mcp model-context-protocol finance stocks trading technical-analysis market-data yfinance",
    project_urls={
        "Bug Reports": "https://github.com/akshatbindal/finance-mcp-server/issues",
        "Source": "https://github.com/akshatbindal/finance-mcp-server",
        "Documentation": "https://github.com/akshatbindal/finance-mcp-server/blob/main/README.md",
        "Changelog": "https://github.com/akshatbindal/finance-mcp-server/blob/main/CHANGELOG.md",
    },
    include_package_data=True,
    zip_safe=False,
)


