import logging
import numpy as np
from datetime import datetime, timedelta
import pandas as pd
from sklearn.ensemble import RandomForestClassifier

class MarketAnalyzer:
    """
    Performs country-specific market analysis including:
    - Trend analysis
    - Sector performance analysis
    - Market sentiment analysis
    - Pattern recognition
    
    The analyzer uses both statistical methods and ML models to identify trading opportunities.
    """
    
    def __init__(self, country_code):
        self.country = country_code
        self.logger = logging.getLogger(f"MarketAnalyzer[{country_code}]")
        
        # Initialize analysis parameters
        self.params = self._get_analysis_params()
        
        # Initialize ML models
        self.models = self._initialize_models()
        
        # Initialize historical data storage
        self.historical_data = {
            "price_history": [],
            "sector_performance": {},
            "market_sentiment": []
        }
        
        # Market conditions cache
        self.market_conditions = {}
        self.last_analysis = None
    
    def _get_analysis_params(self):
        """Get country-specific analysis parameters"""
        params = {
            "india": {
                "trend_periods": [14, 30, 90],  # Days for trend analysis
                "sector_count": 12,  # Number of sectors to track
                "min_volume_ratio": 1.5,  # Minimum volume ratio for confirmation
                "support_resistance_window": 30  # Days for support/resistance
            },
            "us": {
                "trend_periods": [7, 21, 60],
                "sector_count": 11,
                "min_volume_ratio": 1.2,
                "support_resistance_window": 20
            },
            "uk": {
                "trend_periods": [10, 25, 75],
                "sector_count": 10,
                "min_volume_ratio": 1.3,
                "support_resistance_window": 25
            },
            "singapore": {
                "trend_periods": [12, 28, 84],
                "sector_count": 8,
                "min_volume_ratio": 1.4,
                "support_resistance_window": 22
            }
        }
        return params.get(self.country, params["us"])  # Default to US parameters
    
    def _initialize_models(self):
        """Initialize ML models for pattern recognition"""
        models = {
            "trend_prediction": RandomForestClassifier(n_estimators=100),
            "sector_rotation": RandomForestClassifier(n_estimators=100),
            "reversal_detection": RandomForestClassifier(n_estimators=100)
        }
        
        # In production, these would be pre-trained
        # For now, we'll just initialize them
        
        return models
    
    def analyze_market_trend(self, normalized_data):
        """
        Analyze overall market trend using multiple timeframes
        
        Args:
            normalized_data: Standardized market data
            
        Returns:
            dict: Trend analysis results
        """
        self.logger.info("Analyzing market trend")
        
        # Extract relevant data
        index_data = normalized_data["index"]
        sector_data = normalized_data["sectors"]
        market_summary = normalized_data["market_summary"]
        
        # Calculate trend across multiple timeframes
        trend_analysis = self._calculate_trend(index_data)
        
        # Analyze sector leadership
        sector_leadership = self._analyze_sector_leadership(sector_data)
        
        # Check market breadth
        market_breadth = self._analyze_market_breadth(normalized_data)
        
        # Check sentiment
        sentiment = self._analyze_sentiment(normalized_data)
        
        # Determine overall trend
        overall_trend = self._determine_overall_trend(trend_analysis, sector_leadership, market_breadth, sentiment)
        
        # Update market conditions cache
        self.market_conditions["trend"] = overall_trend
        self.last_analysis = datetime.now().isoformat()
        
        return {
            "trend": overall_trend,
            "confidence": trend_analysis["confidence"],
            "key_driver": trend_analysis["key_driver"],
            "sector_leadership": sector_leadership,
            "market_breadth": market_breadth,
            "sentiment": sentiment,
            "timestamp": datetime.now().isoformat()
        }
    
    def _calculate_trend(self, index_data):
        """Calculate market trend using multiple timeframes"""
        # This would use actual historical data in production
        # For demonstration, we'll return a simulated trend
        
        # Simulate different trend signals
        short_term = np.random.choice(["up", "down", "neutral"], p=[0.4, 0.3, 0.3])
        medium_term = np.random.choice(["up", "down", "neutral"], p=[0.3, 0.4, 0.3])
        long_term = np.random.choice(["up", "down", "neutral"], p=[0.6, 0.2, 0.2])
        
        # Calculate confidence based on trend alignment
        trends = [short_term, medium_term, long_term]
        confidence = trends.count("up") / len(trends) if "up" in trends else 0.5
        
        return {
            "short_term": short_term,
            "medium_term": medium_term,
            "long_term": long_term,
            "overall": self._get_overall_trend(trends),
            "confidence": confidence,
            "key_driver": self._generate_key_driver(trends)
        }
    
    def _get_overall_trend(self, trends):
        """Determine overall trend from multiple timeframe analysis"""
        up_count = trends.count("up")
        down_count = trends.count("down")
        
        if up_count > down_count:
            return "bullish"
        elif down_count > up_count:
            return "bearish"
        else:
            return "neutral"
    
    def _generate_key_driver(self, trends):
        """Generate a key driver explanation for the trend"""
        if trends[0] == "up" and trends[1] == "up" and trends[2] == "up":
            return "Strong upward momentum across all timeframes"
        elif trends[0] == "down" and trends[1] == "down" and trends[2] == "down":
            return "Sustained downward pressure across all timeframes"
        elif trends[0] == "up":
            return "Short-term bullish momentum"
        elif trends[0] == "down":
            return "Short-term bearish pressure"
        else:
            return "Mixed signals with no clear direction"
    
    def _analyze_sector_leadership(self, sector_data):
        """Analyze sector performance to identify leadership"""
        if not sector_data:
            return {
                "top_sectors": [],
                "rotation_pattern": "neutral",
                "confidence": 0.5
            }
        
        # Sort sectors by performance
        sorted_sectors = sorted(sector_data, key=lambda x: x.get("change_percent", 0), reverse=True)
        
        # Get top 3 sectors
        top_sectors = sorted_sectors[:3]
        
        # Determine rotation pattern
        rotation = self._determine_rotation_pattern(sorted_sectors)
        
        return {
            "top_sectors": top_sectors,
            "rotation_pattern": rotation,
            "confidence": 0.7 if rotation != "neutral" else 0.5
        }
    
    def _determine_rotation_pattern(self, sorted_sectors):
        """Determine sector rotation pattern"""
        if len(sorted_sectors) < 5:
            return "neutral"
        
        # Check if leadership is concentrated in few sectors
        top3_sum = sum([s["change_percent"] for s in sorted_sectors[:3]])
        bottom3_sum = sum([s["change_percent"] for s in sorted_sectors[-3:]])
        
        if top3_sum > 0 and bottom3_sum < 0:
            return "concentrated"
        elif top3_sum > 0 and bottom3_sum > 0:
            return "broad"
        elif top3_sum < 0 and bottom3_sum < 0:
            return "broad_down"
        else:
            return "neutral"
    
    def _analyze_market_breadth(self, normalized_data):
        """Analyze market breadth (advancing vs declining issues)"""
        gainers = len(normalized_data["top_gainers"])
        losers = len(normalized_data["top_losers"])
        
        if gainers == 0 and losers == 0:
            return {
                "advance_decline": 0,
                "breadth_score": 0.5,
                "strength": "neutral"
            }
        
        # Calculate advance-decline ratio
        ad_ratio = gainers / (gainers + losers) if (gainers + losers) > 0 else 0.5
        breadth_score = 2 * (ad_ratio - 0.5)
        
        # Determine strength
        if breadth_score > 0.3:
            strength = "strong"
        elif breadth_score > 0.1:
            strength = "moderate"
        elif breadth_score < -0.3:
            strength = "weak"
        elif breadth_score < -0.1:
            strength = "moderately_weak"
        else:
            strength = "neutral"
        
        return {
            "advance_decline": ad_ratio,
            "breadth_score": breadth_score,
            "strength": strength,
            "gainers": gainers,
            "losers": losers
        }
    
    def _analyze_sentiment(self, normalized_data):
        """Analyze market sentiment from news and social media"""
        # In production, this would use NLP on news content
        # For demonstration, we'll simulate sentiment
        
        # Get news insights
        news_insights = normalized_data["market_summary"].get("news_insights", [])
        
        # Get expert opinions
        expert_opinions = normalized_data["market_summary"].get("expert_opinions", [])
        
        # Calculate sentiment score
        sentiment_score = 0.5  # Neutral default
        
        if news_insights:
            # Simple sentiment analysis (in production, use NLP)
            positive_keywords = ['strong', 'growth', 'up', 'bullish', 'positive', 'outperform']
            negative_keywords = ['weak', 'decline', 'down', 'bearish', 'negative', 'underperform']
            
            content = " ".join([insight.get("content", "") for insight in news_insights])
            content_lower = content.lower()
            
            positive_count = sum(1 for word in positive_keywords if word in content_lower)
            negative_count = sum(1 for word in negative_keywords if word in content_lower)
            
            total = positive_count + negative_count
            if total > 0:
                sentiment_score = (positive_count - negative_count) / total
                sentiment_score = (sentiment_score + 1) / 2  # Normalize to 0-1
        
        # Incorporate expert opinions
        if expert_opinions:
            expert_sentiment = np.mean([op.get("confidence", 0.7) * (1 if "bullish" in op.get("opinion", "").lower() else 0) for op in expert_opinions])
            sentiment_score = (sentiment_score * 0.7) + (expert_sentiment * 0.3)
        
        # Determine sentiment category
        if sentiment_score > 0.7:
            sentiment = "bullish"
        elif sentiment_score > 0.55:
            sentiment = "moderately_bullish"
        elif sentiment_score < 0.3:
            sentiment = "bearish"
        elif sentiment_score < 0.45:
            sentiment = "moderately_bearish"
        else:
            sentiment = "neutral"
        
        return {
            "score": sentiment_score,
            "sentiment": sentiment,
            "news_count": len(news_insights),
            "expert_count": len(expert_opinions)
        }
    
    def _determine_overall_trend(self, trend_analysis, sector_leadership, market_breadth, sentiment):
        """Determine overall market trend from multiple factors"""
        # Weighted combination of factors
        weights = {
            "trend": 0.4,
            "sector": 0.25,
            "breadth": 0.2,
            "sentiment": 0.15
        }
        
        # Calculate score for each factor
        trend_score = 0.5  # Neutral
        if trend_analysis["overall"] == "bullish":
            trend_score = 0.7
        elif trend_analysis["overall"] == "bearish":
            trend_score = 0.3
        
        sector_score = 0.5  # Neutral
        if sector_leadership["rotation_pattern"] == "concentrated":
            sector_score = 0.7 if trend_score > 0.5 else 0.3
        elif sector_leadership["rotation_pattern"] == "broad":
            sector_score = 0.65 if trend_score > 0.5 else 0.35
        
        breadth_score = market_breadth["breadth_score"] + 0.5  # Shift to 0-1 scale
        
        sentiment_score = sentiment["score"]
        
        # Calculate weighted average
        overall_score = (
            trend_score * weights["trend"] +
            sector_score * weights["sector"] +
            breadth_score * weights["breadth"] +
            sentiment_score * weights["sentiment"]
        )
        
        # Determine final trend
        if overall_score > 0.65:
            return "bullish"
        elif overall_score > 0.55:
            return "moderately_bullish"
        elif overall_score < 0.35:
            return "bearish"
        elif overall_score < 0.45:
            return "moderately_bearish"
        else:
            return "neutral"
    
    def identify_trading_opportunities(self, normalized_data, analysis_results=None):
        """
        Identify specific trading opportunities based on market analysis
        
        Args:
            normalized_data: Standardized market data
            analysis_results: Optional pre-computed analysis results
            
        Returns:
            list: Trading opportunities with entry/exit parameters
        """
        if not analysis_results:
            analysis_results = self.analyze_market_trend(normalized_data)
        
        # Identify opportunities based on trend and sector analysis
        opportunities = []
        
        # Get top-performing sectors
        top_sectors = [s["name"] for s in analysis_results["sector_leadership"]["top_sectors"][:2]]
        
        # Get market trend
        trend = analysis_results["trend"]
        
        # Identify stocks in top sectors with strong technicals
        for sector in top_sectors:
            sector_stocks = self._identify_strong_stocks_in_sector(normalized_data, sector)
            
            for stock in sector_stocks[:5]:  # Take top 5 from each sector
                opportunity = self._create_trading_opportunity(stock, trend)
                opportunities.append(opportunity)
        
        # Add contrarian opportunities if market is extreme
        if trend in ["bullish", "bearish"] and analysis_results["confidence"] > 0.7:
            contrarian = self._identify_contrarian_opportunities(normalized_data, trend)
            opportunities.extend(contrarian)
        
        return opportunities
    
    def _identify_strong_stocks_in_sector(self, normalized_data, sector_name):
        """Identify strong stocks within a specific sector"""
        # In production, this would analyze individual stock data
        # For demonstration, we'll return placeholder data
        
        # Simulate finding 5 strong stocks in the sector
        return [
            {"symbol": f"STK{i}", "name": f"Stock {i}", "sector": sector_name, "change": np.random.uniform(0.02, 0.05)}
            for i in range(1, 6)
        ]
    
    def _create_trading_opportunity(self, stock, trend):
        """Create a trading opportunity from stock data and trend"""
        # Calculate entry, target, and stop loss
        entry = stock["change"] * 100  # Placeholder
        target = entry * (1 + np.random.uniform(0.02, 0.04))
        stop_loss = entry * (1 - np.random.uniform(0.01, 0.02))
        
        # Determine timeframe based on trend
        if trend == "bullish":
            timeframe = "intraday"
        elif trend == "moderately_bullish":
            timeframe = "btst"
        else:
            timeframe = "swt"
        
        return {
            "symbol": stock["symbol"],
            "name": stock["name"],
            "sector": stock["sector"],
            "entry_zone": f"{entry:.2f}-{entry*1.01:.2f}",
            "target": target,
            "stop_loss": stop_loss,
            "timeframe": timeframe,
            "confidence": np.random.uniform(0.7, 0.9)
        }
    
    def _identify_contrarian_opportunities(self, normalized_data, trend):
        """Identify contrarian trading opportunities"""
        # In production, this would look for oversold/overbought conditions
        # For demonstration, we'll return placeholder data
        
        if trend == "bullish":
            # Look for oversold stocks
            return [
                {
                    "symbol": "OVERSOLD1",
                    "name": "Oversold Stock 1",
                    "sector": "Energy",
                    "entry_zone": "100.00-101.00",
                    "target": 105.00,
                    "stop_loss": 98.50,
                    "timeframe": "swt",
                    "confidence": 0.75
                }
            ]
        else:
            # Look for overbought stocks
            return [
                {
                    "symbol": "OVERBOUGHT1",
                    "name": "Overbought Stock 1",
                    "sector": "Technology",
                    "entry_zone": "200.00-201.00",
                    "target": 195.00,
                    "stop_loss": 202.50,
                    "timeframe": "swt",
                    "confidence": 0.7
                }
            ]
    
    def analyze_technical_indicators(self, normalized_data):
        """
        Analyze technical indicators for all stocks
        
        Args:
            normalized_data: Standardized market data
            
        Returns:
            dict: Technical analysis results
        """
        self.logger.info("Analyzing technical indicators")
        
        # In production, this would process historical price data
        # For demonstration, we'll return simulated technical analysis
        
        # Simulate technical analysis for top 10 stocks
        technical_analysis = {}
        
        for i in range(1, 11):
            symbol = f"STK{i}"
            technical_analysis[symbol] = {
                "momentum": np.random.uniform(0.6, 1.0),
                "volume_confirmation": np.random.uniform(0.5, 1.0),
                "support_resistance": np.random.uniform(0.6, 1.0),
                "relative_strength": np.random.uniform(0.5, 1.0),
                "pattern_recognition": np.random.choice(["none", "head_and_shoulders", "double_top", "cup_and_handle"], p=[0.7, 0.1, 0.1, 0.1])
            }
        
        return technical_analysis
    
    def get_market_conditions(self):
        """
        Get current market conditions
        
        Returns:
            dict: Current market conditions
        """
        if not self.market_conditions or (datetime.now() - datetime.fromisoformat(self.last_analysis)).total_seconds() > 300:
            # If conditions are stale, refresh them
            self.analyze_market_trend(self._get_sample_data())
        
        return self.market_conditions
    
    def _get_sample_data(self):
        """Get sample data for demonstration purposes"""
        return {
            "timestamp": datetime.now().isoformat(),
            "country": self.country,
            "exchange": "Sample Exchange",
            "index": {
                "name": "Sample Index",
                "value": 1000.0,
                "change": 10.0,
                "change_percent": 1.0,
                "volume": "1000000"
            },
            "sectors": [
                {"name": "Sector 1", "change_percent": 2.0},
                {"name": "Sector 2", "change_percent": 1.5},
                {"name": "Sector 3", "change_percent": 1.0}
            ],
            "top_gainers": [
                {"symbol": "GAINER1", "change_percent": 5.0},
                {"symbol": "GAINER2", "change_percent": 4.5}
            ],
            "top_losers": [
                {"symbol": "LOSER1", "change_percent": -4.0},
                {"symbol": "LOSER2", "change_percent": -3.5}
            ],
            "market_summary": {
                "fii_dii
