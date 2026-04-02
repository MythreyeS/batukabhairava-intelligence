import logging
import numpy as np
from datetime import datetime, timedelta
import json
import os

class ConvictionScorer:
    """
    Calculates conviction scores for trading recommendations based on:
    - Source credibility
    - Technical analysis
    - Market conditions
    - Historical performance
    
    The conviction score is a weighted combination of these factors (0-1 scale)
    """
    
    def __init__(self, country_code):
        self.country = country_code
        self.logger = logging.getLogger(f"ConvictionScorer[{country_code}]")
        
        # Load configuration
        self.config = self._load_config()
        
        # Initialize scoring weights
        self.scoring_weights = self.config.get("scoring_weights", {
            "source_credibility": 0.6,
            "technical_score": 0.4
        })
        
        # Initialize source weights
        self.source_weights = self._get_source_weights()
        
        # Initialize risk factors
        self.risk_factors = self.config.get("risk_factors", {})
        
        # Initialize credibility database
        self.credibility_db = self._initialize_credibility_db()
        
        # Load historical performance data
        self.historical_data = self._load_historical_performance()
    
    def _load_config(self):
        """Load conviction scoring configuration"""
        config_path = os.path.join(os.path.dirname(__file__), "conviction_config.json")
        
        default_config = {
            "scoring_weights": {
                "source_credibility": 0.6,
                "technical_score": 0.4
            },
            "risk_factors": {
                "market_volatility": {"weight": 0.3, "threshold_high": 0.25},
                "economic_events": {"weight": 0.2, "impact_scale": 1.5},
                "sector_risk": {"weight": 0.15, "max_impact": 0.1}
            },
            "min_conviction": 0.7,
            "max_conviction": 0.95
        }
        
        try:
            if os.path.exists(config_path):
                with open(config_path, 'r') as f:
                    return json.load(f)
            return default_config
        except Exception as e:
            self.logger.error(f"Error loading config: {str(e)}")
            return default_config
    
    def _get_source_weights(self):
        """Get source weights based on country and source type"""
        weights = {
            "india": {
                "primary": {
                    "Finage": 0.9,
                    "AlphaVantage": 0.85
                },
                "secondary": {
                    "NDTV Profit": 0.75,
                    "Moneycontrol": 0.7,
                    "Economic Times": 0.72
                }
            },
            "us": {
                "primary": {
                    "Finnhub": 0.92,
                    "AlphaVantage": 0.88
                },
                "secondary": {
                    "CNBC": 0.78,
                    "Bloomberg": 0.75,
                    "Wall Street Journal": 0.77
                }
            },
            "uk": {
                "primary": {
                    "AlphaVantage": 0.88,
                    "FinancialTimes": 0.85
                },
                "secondary": {
                    "CityAM": 0.7,
                    "Reuters": 0.75,
                    "The Guardian": 0.72
                }
            },
            "singapore": {
                "primary": {
                    "iTick": 0.9,
                    "AlphaVantage": 0.85
                },
                "secondary": {
                    "TheEdgeSingapore": 0.75,
                    "Bloomberg": 0.7,
                    "Straits Times": 0.73
                }
            }
        }
        return weights.get(self.country, weights["us"])  # Default to US weights
    
    def _initialize_credibility_db(self):
        """Initialize source credibility database with default values"""
        credibility_db = {}
        
        # Add all sources from source weights
        for source_type in ["primary", "secondary"]:
            for source_name in self.source_weights[source_type].keys():
                credibility_db[source_name] = {
                    "base_score": self.source_weights[source_type][source_name],
                    "current_score": self.source_weights[source_type][source_name],
                    "verification_count": 0,
                    "success_count": 0,
                    "last_verified": None,
                    "history": []
                }
        
        return credibility_db
    
    def _load_historical_performance(self):
        """Load historical performance data for backtesting"""
        # In production, this would load from a database
        return {
            "win_rate": 0.65,
            "average_gain": 0.0245,
            "average_loss": -0.0125,
            "sector_performance": {
                "banking": 0.72,
                "technology": 0.68,
                "energy": 0.58
            }
        }
    
    def calculate_conviction(self, source_name, technical_analysis, market_context=None):
        """
        Calculate conviction score for a recommendation
        
        Args:
            source_name: Name of the source providing the recommendation
            technical_analysis: Dict containing technical analysis metrics
            market_context: Current market conditions (optional)
            
        Returns:
            float: Conviction score between 0-1
        """
        # 1. Calculate source credibility score
        source_score = self._calculate_source_score(source_name)
        
        # 2. Calculate technical score
        technical_score = self._calculate_technical_score(technical_analysis)
        
        # 3. Calculate risk adjustment
        risk_adjustment = self._calculate_risk_adjustment(market_context)
        
        # 4. Calculate final conviction
        conviction = (source_score * self.scoring_weights["source_credibility"] +
                     technical_score * self.scoring_weights["technical_score"])
        
        # Apply risk adjustment (capped between min and max)
        conviction = max(self.config["min_conviction"], 
                        min(self.config["max_conviction"], conviction - risk_adjustment))
        
        return conviction
    
    def _calculate_source_score(self, source_name):
        """Calculate source credibility score"""
        # Determine if primary or secondary source
        for source_type in ["primary", "secondary"]:
            if source_name in self.source_weights[source_type]:
                base_score = self.source_weights[source_type][source_name]
                # Add time decay factor (newer = better)
                time_decay = 0.05  # 5% maximum decay for older sources
                return base_score * (1 - time_decay)
        
        # Default score for unknown sources
        return 0.6
    
    def _calculate_technical_score(self, technical_analysis):
        """Calculate technical analysis score"""
        if not technical_analysis:
            return 0.5  # Default score if no technical analysis
        
        # Weighted average of technical metrics
        weights = {
            "momentum": 0.25,
            "volume_confirmation": 0.20,
            "support_resistance": 0.25,
            "sector_strength": 0.15,
            "historical_success": 0.15
        }
        
        score = 0
        for metric, value in technical_analysis.items():
            if metric in weights:
                # Normalize value to 0-1 scale if needed
                normalized_value = min(1.0, max(0.0, value))
                score += normalized_value * weights[metric]
        
        return score
    
    def _calculate_risk_adjustment(self, market_context=None):
        """Calculate risk adjustment based on market conditions"""
        if not market_context:
            # Default risk adjustment when context not provided
            return np.random.uniform(0, 0.15)
        
        adjustment = 0
        
        # Apply risk factors
        for factor, config in self.risk_factors.items():
            if factor in market_context:
                impact = market_context[factor] * config["weight"]
                adjustment += min(impact, config.get("max_impact", 0.15))
        
        return adjustment
    
    def generate_recommendation_metadata(self, source_name, technical_analysis, market_context=None):
        """Generate complete metadata for a recommendation"""
        conviction = self.calculate_conviction(source_name, technical_analysis, market_context)
        
        return {
            "source": source_name,
            "source_credibility": self._calculate_source_score(source_name),
            "technical_score": self._calculate_technical_score(technical_analysis),
            "conviction_score": conviction,
            "risk_adjustment": self._calculate_risk_adjustment(market_context),
            "timestamp": datetime.now().isoformat(),
            "country": self.country,
            "market_context": market_context or {}
        }
    
    def update_source_credibility(self, source_name, was_correct):
        """
        Update source credibility based on recommendation outcome
        
        Args:
            source_name: Name of the source
            was_correct: Whether the recommendation was correct
        """
        if source_name not in self.credibility_db:
            self.logger.warning(f"Unknown source: {source_name}")
            return
        
        # Update database
        source = self.credibility_db[source_name]
        source["verification_count"] += 1
        
        if was_correct:
            source["success_count"] += 1
        
        # Update current score with exponential smoothing
        alpha = 0.2  # Smoothing factor
        success_rate = source["success_count"] / source["verification_count"]
        source["current_score"] = (
            source["current_score"] * (1 - alpha) + 
            success_rate * alpha
        )
        
        # Cap score between 0.5 and 0.95
        source["current_score"] = max(0.5, min(0.95, source["current_score"]))
        
        # Record in history
        source["history"].append({
            "timestamp": datetime.now().isoformat(),
            "was_correct": was_correct,
            "current_score": source["current_score"],
            "success_rate": success_rate
        })
        
        # Keep only recent history
        max_history = 50
        if len(source["history"]) > max_history:
            source["history"] = source["history"][-max_history:]
        
        # Update last verified timestamp
        source["last_verified"] = datetime.now().isoformat()
        
        self.logger.info(
            f"Updated credibility for {source_name}: {source['current_score']:.2f} "
            f"(prev: {source['current_score']/(1-alpha) - success_rate*alpha/(1-alpha):.2f})"
        )
    
    def get_source_credibility_report(self):
        """Generate a credibility report for all sources"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "country": self.country,
            "sources": {}
        }
        
        for source_name, data in self.credibility_db.items():
            report["sources"][source_name] = {
                "current_score": data["current_score"],
                "base_score": data["base_score"],
                "verification_count": data["verification_count"],
                "success_rate": (
                    data["success_count"] / max(data["verification_count"], 1)
                    if data["verification_count"] > 0 else 0.0
                ),
                "last_verified": data["last_verified"]
            }
        
        # Add summary statistics
        scores = [d["current_score"] for d in report["sources"].values()]
        report["summary"] = {
            "average_score": np.mean(scores) if scores else 0.0,
            "highest_score": max(scores) if scores else 0.0,
            "lowest_score": min(scores) if scores else 0.0
        }
        
        return report
    
    def get_recommended_sources(self, min_score=0.7):
        """Get sources above a minimum credibility score"""
        return [
            source for source, data in self.credibility_db.items()
            if data["current_score"] >= min_score
        ]
