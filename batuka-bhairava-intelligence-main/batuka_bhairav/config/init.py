"""
MarketPulse Configuration Package

This package contains all configuration files for the multi-agent trading intelligence platform.

Core Components:
- market_hours.py: Market hours for all countries
- sources.py: Data source configurations with reliability weights

The configuration package provides a centralized location for all system settings and parameters.

__all__ = [
    'MARKET_HOURS',
    'DATA_SOURCES',
    'get_market_hours',
    'get_data_sources'
]

__version__ = "1.0.0"
__author__ = "MarketPulse Development Team"
__description__ = "Configuration for multi-agent trading intelligence platform"

# Import all modules for convenient access
from .market_hours import MARKET_HOURS, get_market_hours
from .sources import DATA_SOURCES, get_data_sources

def initialize_configuration():
    """
    Initialize and validate all configuration data
    
    Returns:
        dict: Combined configuration data
    """
    config = {
        "market_hours": MARKET_HOURS,
        "data_sources": DATA_SOURCES
    }
    
    # Validate configuration
    if not validate_configuration(config):
        raise ValueError("Configuration validation failed")
    
    return config

def validate_configuration(config):
    """
    Validate configuration data
    
    Args:
        config (dict): Configuration data to validate
        
    Returns:
        bool: True if configuration is valid
    """
    # Check market hours
    required_market_fields = ["open", "close", "timezone"]
    for country, hours in config["market_hours"].items():
        if not all(field in hours for field in required_market_fields):
            return False
    
    # Check data sources
    required_source_fields = ["name", "api", "weight", "type"]
    for country, sources in config["data_sources"].items():
        for source_type in ["primary", "secondary"]:
            for source in sources[source_type]:
                if not all(field in source for field in required_source_fields):
                    return False
    
    return True
