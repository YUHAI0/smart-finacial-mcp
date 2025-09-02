"""
Tushare MCP - 基于Model Context Protocol的智能股票数据助手

提供与AI助手自然对话获取股票数据的能力，支持股票、ETF、指数、期货等多种金融数据查询。
"""

__version__ = "1.0.0"
__author__ = "yuhai"
__email__ = "me.yuhai@hotmail.com"
__license__ = "MIT"

from .server import main

__all__ = ["main"]
