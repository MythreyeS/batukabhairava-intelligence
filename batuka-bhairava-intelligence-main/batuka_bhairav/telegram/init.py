"""
MarketPulse Telegram Integration Package

This package contains all components for Telegram bot integration, including:
- Message formatting
- Scheduling
- Bot implementation
- User interaction handling

The package provides a seamless interface between the trading intelligence platform and Telegram users.

__all__ = [
    'TelegramFormatter',
    'ReportScheduler',
    'TradingTelegramBot'
]

__version__ = "1.0.0"
__author__ = "MarketPulse Development Team"
__description__ = "Telegram integration for multi-agent trading intelligence platform"

# Import all modules for convenient access
from .formatter import TelegramFormatter
from .scheduler import ReportScheduler
from .bot import TradingTelegramBot

def initialize_telegram_integration(agents):
    """
    Initialize all Telegram integration components
    
    Args:
        agents (dict): Dictionary of country-specific agents
        
    Returns:
        tuple: (TradingTelegramBot, ReportScheduler) instances
    """
    formatter = TelegramFormatter()
    scheduler = ReportScheduler(agents)
    bot = TradingTelegramBot(None, agents)  # Token will be set later
    
    return bot, scheduler
