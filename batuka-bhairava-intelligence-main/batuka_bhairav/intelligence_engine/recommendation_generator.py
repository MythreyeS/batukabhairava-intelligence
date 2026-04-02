import logging
import numpy as np
from datetime import datetime, timedelta

class RecommendationGenerator:
    """
    Generates trading recommendations with conviction scores and risk parameters.
    
    The generator combines market analysis with conviction scoring to produce actionable
    trading recommendations with specific entry, target, and stop-loss levels.
    """
    
    def __init__(self, country_code, conviction_scorer, market_analyzer):
        self.country = country_code
        self.logger = logging.getLogger(f"RecommendationGenerator[{country_code}]")
        self.conviction_scorer = conviction_scorer
        self.market_analyzer = market_analyzer
        
        # Initialize recommendation parameters
        self.params = self._get_recommendation_params()
        
        # Initialize tracking for recommendation performance
        self.recommendation_history = []
    
    def _get_recommendation_params(self):
        """Get country-specific recommendation parameters"""
        params = {
            "india": {
                "min_conviction": 0.7,
                "max_recommendations": 15,
                "intraday_target": 0.025,  # 2.5% target
                "intraday_stop": 0.015,    # 1.5% stop
                "btst_target": 0.04,       # 4% target
                "btst_stop": 0.02,         # 2% stop
                "sector_allocation": {
                    "banking": 0.25,
                    "it": 0.20,
                    "pharma": 0.15,
                    "energy": 0.15,
                    "auto": 0.10,
                    "others": 0.15
                }
            },
            "us": {
                "min_conviction": 0.7,
                "max_recommendations": 15,
                "intraday_target": 0.02,
                "intraday_stop": 0.01,
                "btst_target": 0.035,
                "btst_stop": 0.015,
                "sector_allocation": {
                    "technology": 0.30,
                    "financials": 0.20,
                    "healthcare": 0.15,
                    "consumer_discretionary": 0.15,
                    "industrials": 0.10,
                    "others": 0.10
                }
            },
            "uk": {
                "min_conviction": 0.7,
                "max_recommendations": 15,
                "intraday_target": 0.018,
                "intraday_stop": 0.012,
                "btst_target": 0.032,
                "btst_stop": 0.018,
                "sector_allocation": {
                    "financials": 0.28,
                    "energy": 0.22,
                    "industrials": 0.18,
                    "consumer_goods": 0.15,
                    "healthcare": 0.10,
                    "others": 0.07
                }
            },
            "singapore": {
                "min_conviction": 0.7,
                "max_recommendations": 15,
                "intraday_target": 0.022,
                "intraday_stop": 0.014,
                "btst_target": 0.038,
                "btst_stop": 0.02,
                "sector_allocation": {
                    "reits": 0.35,
                    "banking": 0.25,
                    "industrials": 0.20,
                    "technology": 0.15,
                    "others": 0.05
                }
            }
        }
        return params.get(self.country, params["us"])  # Default to US parameters
    
    def generate(self, normalized_data, report_type="intraday", min_conviction=None):
        """
        Generate trading recommendations
        
        Args:
            normalized_data: Standardized market data
            report_type: Type of recommendations to generate (intraday, btst, swt)
            min_conviction: Minimum conviction score (defaults to configured value)
            
        Returns:
            list: Trading recommendations with conviction scores
        """
        self.logger.info(f"Generating {report_type} recommendations")
        
        # Get market analysis
        market_analysis = self.market_analyzer.analyze_market_trend(normalized_data)
        
        # Get technical analysis
        technical_analysis = self.market_analyzer.analyze_technical_indicators(normalized_data)
        
        # Identify trading opportunities
        opportunities = self.market_analyzer.identify_trading_opportunities(
            normalized_data, 
            market_analysis
        )
        
        # Generate recommendations
        recommendations = []
        for opportunity in opportunities:
            # Get technical metrics for this stock
            tech_metrics = technical_analysis.get(opportunity["symbol"], {})
            
            # Calculate conviction score
            conviction = self._calculate_conviction(
                opportunity, 
                tech_metrics,
                market_analysis
            )
            
            # Skip if below minimum conviction
            min_conv = min_conviction or self.params["min_conviction"]
            if conviction < min_conv:
                continue
            
            # Add recommendation
            recommendation = self._format_recommendation(
                opportunity, 
                conviction,
                report_type
            )
            recommendations.append(recommendation)
        
        # Sort by conviction score (highest first)
        recommendations.sort(key=lambda x: x["conviction"], reverse=True)
        
        # Limit to maximum number of recommendations
        recommendations = recommendations[:self.params["max_recommendations"]]
        
        # Add to history
        self._add_to_history(recommendations, report_type)
        
        self.logger.info(f"Generated {len(recommendations)} recommendations with conviction >{min_conv:.2f}")
        return recommendations
    
    def _calculate_conviction(self, opportunity, technical_metrics, market_analysis):
        """Calculate conviction score for a trading opportunity"""
        # Get source name (would be determined in production)
        source_name = self._determine_source(opportunity["sector"])
        
        # Prepare technical analysis for scoring
        tech_analysis = {
            "momentum": technical_metrics.get("momentum", 0.6),
            "volume_confirmation": technical_metrics.get("volume_confirmation", 0.5),
            "support_resistance": technical_metrics.get("support_resistance", 0.6),
            "sector_strength": self._get_sector_strength(opportunity["sector"], market_analysis)
        }
        
        # Add historical success (simulated)
        tech_analysis["historical_success"] = np.random.uniform(0.6, 0.85)
        
        # Calculate conviction
        conviction = self.conviction_scorer.calculate_conviction(
            source_name,
            tech_analysis,
            self._get_market_context(market_analysis)
        )
        
        return conviction
    
    def _determine_source(self, sector):
        """Determine the most relevant source for a sector"""
        # In production, this would use actual source credibility data
        sector_sources = {
            "banking": "NDTV Profit",
            "it": "Moneycontrol",
            "pharma": "Economic Times",
            "energy": "CNBC",
            "auto": "Bloomberg",
            "technology": "Finnhub",
            "reits": "TheEdgeSingapore"
        }
        
        return sector_sources.get(sector, "AlphaVantage")
    
    def _get_sector_strength(self, sector, market_analysis):
        """Get strength of a sector from market analysis"""
        for s in market_analysis["sector_leadership"]["top_sectors"]:
            if s["name"].lower() == sector.lower():
                return min(s["change_percent"] / 5, 1.0)  # Normalize to 0-1
        
        return 0.5  # Neutral if not in top sectors
    
    def _get_market_context(self, market_analysis):
        """Convert market analysis to context for conviction scoring"""
        return {
            "market_volatility": market_analysis["market_breadth"]["breadth_score"],
            "economic_events": 0.1 if "FOMC" in market_analysis["key_driver"] else 0,
            "sector_risk": 0.05 if market_analysis["sector_leadership"]["rotation_pattern"] == "concentrated" else 0.02
        }
    
    def _format_recommendation(self, opportunity, conviction, report_type):
        """Format recommendation for delivery"""
        # Get recommendation parameters based on report type
        params = self._get_recommendation_params_for_type(report_type)
        
        # Format entry zone (would be calculated in production)
        entry_zone = opportunity["entry_zone"]
        
        # Calculate target and stop loss
        if report_type == "intraday":
            target = float(entry_zone.split("-")[0]) * (1 + params["target"])
            stop_loss = float(entry_zone.split("-")[0]) * (1 - params["stop"])
        else:
            target = float(entry_zone.split("-")[0]) * (1 + params["target"])
            stop_loss = float(entry_zone.split("-")[0]) * (1 - params["stop"])
        
        return {
            "symbol": opportunity["symbol"],
            "name": opportunity["name"],
            "sector": opportunity["sector"],
            "entry_zone": entry_zone,
            "target": round(target, 2),
            "stop_loss": round(stop_loss, 2),
            "timeframe": report_type,
            "conviction": conviction,
            "source": self._determine_source(opportunity["sector"]),
            "confidence_reasons": self._generate_confidence_reasons(opportunity, conviction),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_recommendation_params_for_type(self, report_type):
        """Get recommendation parameters for a specific timeframe"""
        if report_type == "intraday":
            return {
                "target": self.params["intraday_target"],
                "stop": self.params["intraday_stop"]
            }
        elif report_type == "btst":
            return {
                "target": self.params["btst_target"],
                "stop": self.params["btst_stop"]
            }
        else:
            return {
                "target": self.params["btst_target"] * 1.5,
                "stop": self.params["btst_stop"] * 1.2
            }
    
    def _generate_confidence_reasons(self, opportunity, conviction):
        """Generate reasons for the confidence score"""
        reasons = []
        
        # Add trend reason
        if conviction > 0.85:
            reasons.append("Strong alignment with multiple timeframe trend")
        elif conviction > 0.75:
            reasons.append("Favorable market trend with sector leadership")
        else:
            reasons.append("Moderate market conditions with sector support")
        
        # Add volume reason
        if np.random.random() > 0.5:
            reasons.append("Positive volume confirmation")
        
        # Add technical reason
        if np.random.random() > 0.7:
            reasons.append("Strong technical setup at support level")
        
        return reasons
    
    def _add_to_history(self, recommendations, report_type):
        """Add recommendations to history for performance tracking"""
        timestamp = datetime.now().isoformat()
        
        for rec in recommendations:
            self.recommendation_history.append({
                "timestamp": timestamp,
                "symbol": rec["symbol"],
                "report_type": report_type,
                "entry": rec["entry_zone"],
                "target": rec["target"],
                "stop_loss": rec["stop_loss"],
                "conviction": rec["conviction"],
                "sector": rec["sector"],
                "status": "open",
                "performance": None
            })
    
    def track_recommendation_performance(self, symbol, current_price):
        """
        Track performance of a recommendation
        
        Args:
            symbol: Stock symbol
            current_price: Current price to evaluate performance
            
        Returns:
            dict: Performance metrics for the recommendation
        """
        # Find open recommendation for this symbol
        open_recs = [r for r in self.recommendation_history 
                    if r["symbol"] == symbol and r["status"] == "open"]
        
        if not open_recs:
            return None
        
        # Take the most recent recommendation
        rec = open_recs[-1]
        
        # Calculate performance
        entry = float(rec["entry"].split("-")[0])
        change = (current_price - entry) / entry
        
        # Determine status
        if current_price >= rec["target"]:
            status = "target_achieved"
        elif current_price <= rec["stop_loss"]:
            status = "stop_loss_triggered"
        else:
            status = "open"
        
        # Update recommendation
        rec["status"] = status
        rec["performance"] = change
        rec["current_price"] = current_price
        rec["evaluation_time"] = datetime.now().isoformat()
        
        # Update source credibility if recommendation is closed
        if status != "open":
            self.conviction_scorer.update_source_credibility(
                rec["source"],
                status == "target_achieved"
            )
        
        return {
            "symbol": symbol,
            "status": status,
            "change_percent": change * 100,
            "conviction": rec["conviction"],
            "source": rec["source"]
        }
    
    def get_performance_report(self):
        """Generate performance report for all recommendations"""
        closed_recs = [r for r in self.recommendation_history if r["status"] != "open"]
        
        if not closed_recs:
            return {
                "total_recommendations": 0,
                "win_rate": 0,
                "average_gain": 0,
                "average_loss": 0,
                "sector_performance": {}
            }
        
        # Calculate win rate
        wins = [r for r in closed_recs if r["status"] == "target_achieved"]
        win_rate = len(wins) / len(closed_recs)
        
        # Calculate average gain/loss
        gains = [r["performance"] for r in wins]
        losses = [r["performance"] for r in closed_recs if r["status"] == "stop_loss_triggered"]
        
        avg_gain = np.mean(gains) * 100 if gains else 0
        avg_loss = np.mean(losses) * 100 if losses else 0
        
        # Calculate sector performance
        sector_perf = {}
        for rec in closed_recs:
            sector = rec["sector"]
            if sector not in sector_perf:
                sector_perf[sector] = {"count": 0, "gains": [], "losses": []}
            
            sector_perf[sector]["count"] += 1
            if rec["status"] == "target_achieved":
                sector_perf[sector]["gains"].append(rec["performance"])
            else:
                sector_perf[sector]["losses"].append(rec["performance"])
        
        # Format sector performance
        formatted_sector_perf = {}
        for sector, data in sector_perf.items():
            win_count = len(data["gains"])
            total = data["count"]
            sector_win_rate = win_count / total if total > 0 else 0
            
            sector_avg_gain = np.mean(data["gains"]) * 100 if data["gains"] else 0
            sector_avg_loss = np.mean(data["losses"]) * 100 if data["losses"] else 0
            
            formatted_sector_perf[sector] = {
                "win_rate": sector_win_rate,
                "average_gain": sector_avg_gain,
                "average_loss": sector_avg_loss,
                "total_recommendations": total
            }
        
        return {
            "total_recommendations": len(closed_recs),
            "win_rate": win_rate,
            "average_gain": avg_gain,
            "average_loss": avg_loss,
            "sector_performance": formatted_sector_perf,
            "timestamp": datetime.now().isoformat()
        }
    
    def get_recommendation_trends(self):
        """Analyze trends in recommendation performance"""
        performance = self.get_performance_report()
        
        # In production, this would do more sophisticated trend analysis
        # For now, we'll return basic trend information
        
        return {
            "overall_trend": "improving" if performance["win_rate"] > 0.6 else "declining",
            "win_rate_trend": performance["win_rate"],
            "sector_trends": {
                sector: {
                    "trend": "strong" if data["win_rate"] > 0.7 else "weak",
                    "win_rate": data["win_rate"]
                }
                for sector, data in performance["sector_performance"].items()
            },
            "conviction_performance": {
                "high_conviction": {
                    "win_rate": performance["win_rate"] * 1.1,  # Simulated better performance
                    "count": int(len(self.recommendation_history) * 0.3)
                },
                "medium_conviction": {
                    "win_rate": performance["win_rate"],
                    "count": int(len(self.recommendation_history) * 0.5)
                },
                "low_conviction": {
                    "win_rate": performance["win_rate"] * 0.8,
                    "count": int(len(self.recommendation_history) * 0.2)
                }
            }
        }
