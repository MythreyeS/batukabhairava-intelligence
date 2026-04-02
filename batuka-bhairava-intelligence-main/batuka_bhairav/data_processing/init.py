"""
MarketPulse Data Processing Package

This package contains modules for validating, normalizing, and verifying market data from multiple sources.

Core Components:
- validator.py: Data quality validation
- normalizer.py: Standardizes data to a common schema
- source_verification.py: Verifies source credibility and cross-checks information

Usage:
    from data_processing import DataValidator, DataNormalizer, SourceVerifier
    
    validator = DataValidator("india")
    validated_data = validator.validate(raw_data)

The package provides a robust framework for processing market data from diverse sources into a consistent,
reliable format suitable for trading intelligence generation.

__all__ = [
    'DataValidator',
    'DataNormalizer',
    'SourceVerifier'
]

__version__ = "1.0.0"
__author__ = "MarketPulse Development Team"
__description__ = "Data processing framework for multi-agent trading intelligence platform"

# Import all modules for convenient access
from .validator import DataValidator
from .normalizer import DataNormalizer
from .source_verification import SourceVerifier

def initialize_processing_pipeline(country_code):
    """
    Initialize all data processing components for a specific country
    
    Args:
        country_code (str): Country code (e.g., "india", "us")
        
    Returns:
        tuple: (DataValidator, DataNormalizer, SourceVerifier) instances
    """
    validator = DataValidator(country_code)
    normalizer = DataNormalizer(country_code)
    verifier = SourceVerifier(country_code)
    
    return validator, normalizer, verifier
