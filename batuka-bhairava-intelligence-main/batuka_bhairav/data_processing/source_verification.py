import logging
import numpy as np
from datetime import datetime, timedelta
import re
from collections import defaultdict

class SourceVerifier:
    """
    Verifies the credibility of data sources and cross-checks information across multiple sources.
    
    The system tracks source reliability over time and adjusts confidence in recommendations
    based on source quality and consistency with other sources.
    """
    
    def __init__(self, country_code):
        self.country = country_code
        self.logger = logging.getLogger(f"SourceVerifier[{country_code}]")
        
        # Initialize source reliability database
        self.source_reliability = self._initialize_reliability_db()
        
        # Set verification parameters
        self.verification_params = {
            "min_sources": 2,  # Minimum sources required for verification
            "consistency_threshold": 0.8,  # Minimum consistency score
            "recent_weight": 0.7,  # Weight for recent performance
            "historical_weight": 0.3,  # Weight for historical performance
            "max_history_days": 30  # History window for reliability tracking
        }
        
        # Initialize tracking structures
        self.source_performance = defaultdict(list)
        self.verification_history = []
    
    def _initialize_reliability_db(self):
        """
        Initialize source reliability database with default values
        """
        reliability_db = {}
        
        # Default reliability scores based on source type and country
        default_scores = {
            "india": {
                "primary": {
                    "Finage": 0.90,
                    "AlphaVantage": 0.85
                },
                "secondary": {
                    "NDTV Profit": 0.75,
                    "Moneycontrol": 0.70,
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
                    "CityAM": 0.70,
                    "Reuters": 0.75,
                    "The Guardian": 0.72
                }
            },
            "singapore": {
                "primary": {
                    "iTick": 0.90,
                    "AlphaVantage": 0.85
                },
                "secondary": {
                    "TheEdgeSingapore": 0.75,
                    "Bloomberg": 0.70,
                    "Straits Times": 0.73
                }
            }
        }
        
        # Get default scores for this country
        country_scores = default_scores.get(self.country, default_scores["us"])
        
        # Build full reliability database
        for source_type, sources in country_scores.items():
            for source_name, score in sources.items():
                reliability_db[source_name] = {
                    "base_score": score,
                    "current_score": score,
                    "verification_count": 0,
                    "success_count": 0,
                    "last_verified": None,
                    "history": []
                }
        
        return reliability_db
    
    def verify_sources(self, validated_data):
        """
        Verify the consistency and reliability of data across multiple sources
        
        Args:
            validated_data (dict): Data that has already passed validation
            
        Returns:
            dict: Verified data with source credibility metrics
        """
        self.logger.info("Verifying data sources for consistency")
        
        # Process primary sources
        primary_verified = self._verify_primary_sources(validated_data["primary"])
        
        # Process secondary sources
        secondary_verified = self._verify_secondary_sources(validated_data["secondary"])
        
        # Cross-verify between primary and secondary
        cross_verified = self._cross_verify_sources(primary_verified, secondary_verified)
        
        # Update reliability scores
        self._update_reliability_scores(cross_verified)
        
        # Return verified data with credibility metrics
        return {
            "primary": primary_verified,
            "secondary": secondary_verified,
            "cross_verified": cross_verified,
            "source_metrics": self._get_source_metrics()
        }
    
    def _verify_primary_sources(self, primary_data):
        """Verify primary data sources (APIs)"""
        verified = {}
        
        for source_name, data in primary_data.items():
            if source_name not in self.source_reliability:
                continue
                
            # Check if source meets minimum requirements
            if data.get("status") != "success":
                self.logger.warning(f"Source {source_name} reported failure - skipping verification")
                continue
            
            # Calculate verification metrics
            verification_result = self._calculate_verification_metrics(
                source_name, data, "primary"
            )
            
            # Update data with verification info
            verified_data = {
                **data,
                "verification": verification_result,
                "source_reliability": self.source_reliability[source_name]["current_score"]
            }
            
            verified[source_name] = verified_data
        
        return verified
    
    def _verify_secondary_sources(self, secondary_data):
        """Verify secondary data sources (scraped content)"""
        verified = {}
        
        for source_name, data in secondary_data.items():
            if source_name not in self.source_reliability:
                continue
                
            # Check if source meets minimum requirements
            if data.get("status") != "success":
                self.logger.warning(f"Source {source_name} reported failure - skipping verification")
                continue
            
            # Calculate verification metrics
            verification_result = self._calculate_verification_metrics(
                source_name, data, "secondary"
            )
            
            # Update data with verification info
            verified_data = {
                **data,
                "verification": verification_result,
                "source_reliability": self.source_reliability[source_name]["current_score"]
            }
            
            verified[source_name] = verified_data
        
        return verified
    
    def _cross_verify_sources(self, primary_verified, secondary_verified):
        """Cross-verify between primary and secondary sources"""
        cross_verified = {}
        
        # For each primary source, compare with secondary sources
        for primary_source, primary_data in primary_verified.items():
            for secondary_source, secondary_data in secondary_verified.items():
                # Compare key metrics between sources
                comparison = self._compare_source_data(primary_data, secondary_data)
                
                # Store cross-verification results
                key = f"{primary_source}_{secondary_source}"
                cross_verified[key] = {
                    "primary_source": primary_source,
                    "secondary_source": secondary_source,
                    "comparison": comparison,
                    "consistency_score": self._calculate_consistency_score(comparison)
                }
        
        return cross_verified
    
    def _calculate_verification_metrics(self, source_name, data, source_type):
        """Calculate detailed verification metrics for a source"""
        # Base metrics from source reliability
        base_metrics = {
            "source_reliability": self.source_reliability[source_name]["current_score"],
            "verification_time": datetime.now().isoformat(),
            "source_type": source_type,
            "consistent_with": []
        }
        
        # Additional metrics based on source type
        if source_type == "primary":
            # Primary API sources get additional metrics
            base_metrics.update({
                "api_latency": data.get("latency", "N/A"),
                "data_completeness": data.get("completeness", 1.0)
            })
        else:
            # Secondary (scraped) sources get different metrics
            base_metrics.update({
                "content_quality": self._assess_content_quality(data.get("content", "")),
                "sentiment_score": self._extract_sentiment(data.get("content", ""))
            })
        
        return base_metrics
    
    def _compare_source_data(self, source1, source2):
        """Compare data between two sources"""
        comparison = {
            "key_metrics": {},
            "discrepancies": [],
            "consistency_analysis": {}
        }
        
        # Compare index data if available
        if "index" in source1.get("data", {}) and "index" in source2.get("data", {}):
            idx1 = source1["data"]["index"]
            idx2 = source2["data"]["index"]
            
            # Compare value
            if "value" in idx1 and "value" in idx2:
                diff = abs(idx1["value"] - idx2["value"])
                consistency = 1.0 - min(diff / max(idx1["value"], 0.001), 1.0)
                comparison["key_metrics"]["index_value"] = {
                    "value1": idx1["value"],
                    "value2": idx2["value"],
                    "difference": diff,
                    "consistency": consistency
                }
                
                if consistency < 0.8:
                    comparison["discrepancies"].append(
                        f"Index value discrepancy: {diff:.2f} points ({consistency:.0%} consistent)"
                    )
        
        # Add more comparisons as needed
        
        return comparison
    
    def _calculate_consistency_score(self, comparison):
        """Calculate overall consistency score between sources"""
        if not comparison["key_metrics"]:
            return 0.0
        
        # Calculate average consistency across key metrics
        scores = [m["consistency"] for m in comparison["key_metrics"].values()]
        return np.mean(scores)
    
    def _assess_content_quality(self, content):
        """Assess quality of scraped content"""
        if not content:
            return 0.0
        
        # Basic quality metrics
        length_score = min(len(content) / 500, 1.0)  # Content length (max 500 chars)
        structure_score = self._assess_content_structure(content)
        credibility_score = self._assess_credential_indicators(content)
        
        # Weighted average
        return (length_score * 0.4) + (structure_score * 0.3) + (credibility_score * 0.3)
    
    def _assess_content_structure(self, content):
        """Assess structure and readability of content"""
        # Check for proper paragraph structure
        paragraphs = [p for p in content.split('\n') if p.strip()]
        paragraph_score = min(len(paragraphs) / 3, 1.0)
        
        # Check for headline
        has_headline = bool(re.search(r'^#{1,3}\s', content))
        headline_score = 1.0 if has_headline else 0.6
        
        # Check for data points
        data_points = len(re.findall(r'\d{1,3}\.\d{1,2}%', content))
        data_score = min(data_points / 5, 1.0)
        
        return (paragraph_score * 0.4) + (headline_score * 0.3) + (data_score * 0.3)
    
    def _assess_credential_indicators(self, content):
        """Check for credibility indicators in content"""
        # Check for author attribution
        has_author = bool(re.search(r'By\s+[A-Z][a-z]+', content))
        
        # Check for source citations
        has_citations = bool(re.search(r'Source:|According to|Reported by', content))
        
        # Check for publication date
        has_date = bool(re.search(r'\d{1,2}\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)', content))
        
        # Calculate score
        return (has_author * 0.4) + (has_citations * 0.3) + (has_date * 0.3)
    
    def _extract_sentiment(self, content):
        """Basic sentiment extraction from content"""
        if not content:
            return 0.0
        
        # Simple keyword-based sentiment (in production, use NLP model)
        positive_keywords = ['strong', 'growth', 'up', 'bullish', 'positive', 'outperform']
        negative_keywords = ['weak', 'decline', 'down', 'bearish', 'negative', 'underperform']
        
        content_lower = content.lower()
        
        positive_count = sum(1 for word in positive_keywords if word in content_lower)
        negative_count = sum(1 for word in negative_keywords if word in content_lower)
        
        # Calculate sentiment score (-1 to 1)
        total = positive_count + negative_count
        if total == 0:
            return 0.0
        
        return (positive_count - negative_count) / total
    
    def _update_reliability_scores(self, verification_results):
        """Update source reliability scores based on verification results"""
        for verification_id, result in verification_results.items():
            # Get source names from verification ID
            sources = verification_id.split('_')
            primary_source = sources[0]
            secondary_source = sources[1]
            
            # Update both sources
            self._update_single_source(primary_source, result)
            self._update_single_source(secondary_source, result)
    
    def _update_single_source(self, source_name, verification_result):
        """Update reliability score for a single source"""
        if source_name not in self.source_reliability:
            return
            
        reliability = self.source_reliability[source_name]
        consistency = verification_result.get("consistency_score", 0.0)
        
        # Track verification history
        reliability["verification_count"] += 1
        if consistency >= self.verification_params["consistency_threshold"]:
            reliability["success_count"] += 1
        
        # Update current score
        historical_success_rate = reliability["success_count"] / max(reliability["verification_count"], 1)
        recent_weight = self.verification_params["recent_weight"]
        historical_weight = self.verification_params["historical_weight"]
        
        # Calculate new score (80% recent, 20% historical)
        new_score = (
            consistency * recent_weight +
            historical_success_rate * historical_weight
        )
        
        # Apply smoothing to prevent large swings
        smoothing_factor = 0.2
        reliability["current_score"] = (
            reliability["current_score"] * (1 - smoothing_factor) +
            new_score * smoothing_factor
        )
        
        # Cap between 0.5 and 0.95
        reliability["current_score"] = max(0.5, min(0.95, reliability["current_score"]))
        
        # Record in history
        reliability["history"].append({
            "timestamp": datetime.now().isoformat(),
            "consistency": consistency,
            "new_score": reliability["current_score"],
            "verification_count": reliability["verification_count"]
        })
        
        # Prune history to keep only recent entries
        max_history = 50
        if len(reliability["history"]) > max_history:
            reliability["history"] = reliability["history"][-max_history:]
        
        # Update last verified timestamp
        reliability["last_verified"] = datetime.now().isoformat()
        
        self.logger.info(
            f"Updated reliability for {source_name}: {reliability['current_score']:.2f} "
            f"(prev: {reliability['current_score']/(1-smoothing_factor) - new_score*smoothing_factor/(1-smoothing_factor):.2f})"
        )
    
    def _get_source_metrics(self):
        """Get current source reliability metrics"""
        metrics = {}
        
        for source_name, data in self.source_reliability.items():
            metrics[source_name] = {
                "current_reliability": data["current_score"],
                "base_reliability": data["base_score"],
                "verification_count": data["verification_count"],
                "success_rate": (
                    data["success_count"] / max(data["verification_count"], 1)
                    if data["verification_count"] > 0 else 0.0
                ),
                "last_verified": data["last_verified"]
            }
        
        return metrics
    
    def get_reliability_report(self):
        """Generate a comprehensive reliability report for all sources"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "country": self.country,
            "sources": self._get_source_metrics(),
            "summary": {
                "average_reliability": np.mean([m["current_reliability"] for m in self._get_source_metrics().values()]),
                "most_reliable": max(self._get_source_metrics().items(), key=lambda x: x[1]["current_reliability"])[0],
                "least_reliable": min(self._get_source_metrics().items(), key=lambda x: x[1]["current_reliability"])[0]
            }
        }
        
        return report
    
    def get_recommended_sources(self, min_reliability=0.7):
        """Get sources above a minimum reliability threshold"""
        return [
            source for source, metrics in self._get_source_metrics().items()
            if metrics["current_reliability"] >= min_reliability
        ]
