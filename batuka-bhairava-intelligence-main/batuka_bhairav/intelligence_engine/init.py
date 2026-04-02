"""
MarketPulse Intelligence Engine Package

This package contains core components for analyzing market data, generating conviction scores,
and creating trading recommendations.

Core Components:
- conviction_scoring.py: Calculates confidence scores for recommendations
- analysis.py: Performs country-specific market analysis
- recommendation_generator.py: Generates actionable trading recommendations

Usage:
    from intelligence_engine import ConvictionScorer, MarketAnalyzer, RecommendationGenerator
    
    scorer = ConvictionScorer("india")
    confidence = scorer.calculate_conviction("NDTV Profit", technical_analysis)

The package provides a comprehensive framework for transforming market data into actionable intelligence
with quantified confidence levels.

__all__ = [
    'ConvictionScorer',
    'MarketAnalyzer',
    'RecommendationGenerator'
]

__version__ = "1.0.0"
__author__ = "MarketPulse Development Team"
__description__ = "Intelligence engine for multi-agent trading platform"

# Import all modules for convenient access
from .conviction_scoring import ConvictionScorer
from .analysis import MarketAnalyzer
from .recommendation_generator import RecommendationGenerator

def initialize_intelligence_engine(country_code):
    """
    Initialize all intelligence engine components for a specific country
    
    Args:
        country_code (str): Country code (e.g., "india", "us")
        
    Returns:
        tuple: (ConvictionScorer, MarketAnalyzer, RecommendationGenerator) instances
    """
    scorer = ConvictionScorer(country_code)
    analyzer = MarketAnalyzer(country_code)
    generator = RecommendationGenerator(country_code, scorer, analyzer)
    
    return scorer, analyzer, generator
