import logging
from datetime import datetime
import pytz

class DataNormalizer:
    def __init__(self, country_code):
        self.country = country_code
        self.logger = logging.getLogger(f"DataNormalizer[{country_code}]")
        self.standard_schema = self._get_standard_schema()
    
    def _get_standard_schema(self):
        """Define the standard schema for all market data"""
        return {
            "timestamp": None,
            "country": self.country,
            "exchange": None,
            "index": {
                "name": None,
                "value": None,
                "change": None,
                "change_percent": None,
                "volume": None
            },
            "sectors": [],
            "top_gainers": [],
            "top_losers": [],
            "market_summary": {
                "fii_dii_net": None,
                "market_breadth": None,
                "volatility": None,
                "liquidity": None
            },
            "source_metadata": {
                "primary_sources": [],
                "secondary_sources": [],
                "collection_timestamps": {}
            }
        }
    
    def normalize(self, validated_data):
        """Normalize validated data to standard schema"""
        self.logger.info("Normalizing data to standard schema")
        
        # Start with empty standard schema
        normalized = self._create_standard_schema()
        
        # Process primary data sources
        self._process_primary_data(validated_data["primary"], normalized)
        
        # Process secondary data sources
        self._process_secondary_data(validated_data["secondary"], normalized)
        
        # Add metadata
        self._add_metadata(validated_data, normalized)
        
        return normalized
    
    def _create_standard_schema(self):
        """Create a new instance of the standard schema"""
        # Deep copy of the standard schema
        schema = {
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "country": self.country,
            "exchange": self._get_default_exchange(),
            "index": {
                "name": self._get_default_index(),
                "value": None,
                "change": None,
                "change_percent": None,
                "volume": None
            },
            "sectors": [],
            "top_gainers": [],
            "top_losers": [],
            "market_summary": {
                "fii_dii_net": None,
                "market_breadth": None,
                "volatility": None,
                "liquidity": None
            },
            "source_metadata": {
                "primary_sources": [],
                "secondary_sources": [],
                "collection_timestamps": {}
            }
        }
        return schema
    
    def _get_default_exchange(self):
        """Get default exchange for country"""
        exchanges = {
            "india": "NSE/BSE",
            "us": "NYSE/NASDAQ",
            "uk": "LSE",
            "singapore": "SGX"
        }
        return exchanges.get(self.country, "Unknown")
    
    def _get_default_index(self):
        """Get default index for country"""
        indices = {
            "india": "Nifty 50",
            "us": "S&P 500",
            "uk": "FTSE 100",
            "singapore": "STI"
        }
        return indices.get(self.country, "Benchmark Index")
    
    def _process_primary_data(self, primary_data, normalized):
        """Process primary data sources (APIs)"""
        for source_name, data in primary_data.items():
            if data.get("status") != "success":
                continue
                
            # Process index data
            if "index" in data.get("data", {}):
                self._process_index_data(data["data"]["index"], normalized)
            
            # Process sector data
            if "sectors" in data.get("data", {}):
                self._process_sector_data(data["data"]["sectors"], normalized)
            
            # Process top stocks
            if "top_stocks" in data.get("data", {}):
                self._process_top_stocks(data["data"]["top_stocks"], normalized)
            
            # Process market summary
            if "market_summary" in data.get("data", {}):
                self._process_market_summary(data["data"]["market_summary"], normalized)
            
            # Record source
            normalized["source_metadata"]["primary_sources"].append(source_name)
            normalized["source_metadata"]["collection_timestamps"][source_name] = data.get("timestamp")
    
    def _process_secondary_data(self, secondary_data, normalized):
        """Process secondary data sources (scraping)"""
        for source_name, data in secondary_data.items():
            if data.get("status") != "success":
                continue
            
            # Process news content for insights
            if "content" in data:
                self._process_news_content(data["content"], normalized)
            
            # Process expert opinions
            if "expert_opinions" in data:
                self._process_expert_opinions(data["expert_opinions"], normalized)
            
            # Record source
            normalized["source_metadata"]["secondary_sources"].append(source_name)
            normalized["source_metadata"]["collection_timestamps"][source_name] = data.get("timestamp")
    
    def _process_index_data(self, index_data, normalized):
        """Process index data into standard format"""
        normalized["index"]["value"] = index_data.get("value")
        normalized["index"]["change"] = index_data.get("change")
        normalized["index"]["change_percent"] = index_data.get("change_percent")
        normalized["index"]["volume"] = index_data.get("volume")
    
    def _process_sector_data(self, sector_data, normalized):
        """Process sector data into standard format"""
        for sector in sector_data:
            normalized_sector = {
                "name": sector.get("name"),
                "change_percent": sector.get("change_percent"),
                "top_stocks": sector.get("top_stocks", [])[:3]  # Limit to top 3
            }
            normalized["sectors"].append(normalized_sector)
    
    def _process_top_stocks(self, top_stocks, normalized):
        """Process top stocks data"""
        for stock in top_stocks:
            if stock.get("performance", 0) > 0:
                normalized["top_gainers"].append({
                    "symbol": stock["symbol"],
                    "change_percent": stock["performance"]
                })
            else:
                normalized["top_losers"].append({
                    "symbol": stock["symbol"],
                    "change_percent": stock["performance"]
                })
    
    def _process_market_summary(self, market_summary, normalized):
        """Process market summary data"""
        normalized["market_summary"] = {
            **normalized["market_summary"],
            **market_summary
        }
    
    def _process_news_content(self, content, normalized):
        """Process news content for insights"""
        # In production, this would use NLP to extract insights
        # For now, we'll just record that news was processed
        if "news_insights" not in normalized["market_summary"]:
            normalized["market_summary"]["news_insights"] = []
        
        # Add placeholder for actual processing
        normalized["market_summary"]["news_insights"].append({
            "content_length": len(content),
            "processed": True,
            "timestamp": datetime.now().isoformat()
        })
    
    def _process_expert_opinions(self, expert_opinions, normalized):
        """Process expert opinions from news sources"""
        if "expert_opinions" not in normalized["market_summary"]:
            normalized["market_summary"]["expert_opinions"] = []
        
        for opinion in expert_opinions:
            normalized["market_summary"]["expert_opinions"].append({
                "expert": opinion.get("expert"),
                "opinion": opinion.get("opinion"),
                "confidence": opinion.get("confidence", 0.7),
                "source": opinion.get("source", "Unknown")
            })
    
    def _add_metadata(self, validated_data, normalized):
        """Add metadata to normalized data"""
        normalized["source_metadata"]["total_sources"] = (
            len(validated_data["primary"]) + len(validated_data["secondary"])
        )
        normalized["source_metadata"]["verified_sources"] = self._get_source_verification_status(validated_data)
    
    def _get_source_verification_status(self, validated_data):
        """Get verification status for all sources"""
        status = {}
        
        # Add status for primary sources
        for source_name in validated_data["primary"].keys():
            status[source_name] = "verified"  # Would be more detailed in production
        
        # Add status for secondary sources
        for source_name in validated_data["secondary"].keys():
            status[source_name] = "verified"  # Would be more detailed in production
        
        return status
