"""
MarketPulse Trading Intelligence Platform - Agents Package

This package contains all country-specific agents for the multi-agent trading intelligence system.
Each agent is responsible for collecting, processing, and analyzing market data for a specific country.

Available Agents:
- IndiaAgent: Handles Indian market data (BSE/NSE)
- USAgent: Handles US market data (NYSE/NASDAQ)
- UKAgent: Handles UK market data (LSE)
- SingaporeAgent: Handles Singapore market data (SGX)

Usage:
    from agents import IndiaAgent, USAgent, UKAgent, SingaporeAgent
    
    # Initialize agents
    india_agent = IndiaAgent()
    us_agent = USAgent()
"""

# Import all agent classes for convenient access
from .base_agent import BaseAgent
from .india_agent import IndiaAgent
from .us_agent import USAgent
from .uk_agent import UKAgent
from .singapore_agent import SingaporeAgent

# Define what's publicly available when importing the package
__all__ = [
    'BaseAgent',
    'IndiaAgent',
    'USAgent',
    'UKAgent',
    'SingaporeAgent'
]

# Package-level initialization (if needed)
def initialize_agents():
    """
    Initialize all country agents with standard configuration
    
    Returns:
        dict: Dictionary mapping country codes to initialized agent instances
    """
    return {
        "india": IndiaAgent(),
        "us": USAgent(),
        "uk": UKAgent(),
        "singapore": SingaporeAgent()
    }

# Package metadata
__version__ = "1.0.0"
__author__ = "MarketPulse Development Team"
__description__ = "Multi-agent trading intelligence platform for global markets"
