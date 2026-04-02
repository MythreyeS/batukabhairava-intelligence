import logging
from datetime import datetime, timedelta

class DataValidator:
    def __init__(self, country_code):
        self.country = country_code
        self.logger = logging.getLogger(f"DataValidator[{country_code}]")
        self.max_data_age = timedelta(minutes=5)  # Maximum age of acceptable data
        self.required_fields = self._get_required_fields()
    
    def _get_required_fields(self):
        """Get required fields based on country and data type"""
        return {
            "primary": {
                "index": ["value", "change_percent"],
                "sectors": ["name", "change_percent"],
                "top_stocks": ["symbol", "performance"]
            },
            "secondary": {
                "content": ["content"],
                "expert_opinions": ["expert", "opinion"]
            }
        }
    
    def validate(self, raw_data):
        """Validate raw data from all sources"""
        self.logger.info("Validating data from all sources")
        
        # Validate primary data
        validated_primary = self._validate_primary_data(raw_data["primary"])
        
        # Validate secondary data
        validated_secondary = self._validate_secondary_data(raw_data["secondary"])
        
        # Check cross-source consistency
        self._check_consistency(validated_primary, validated_secondary)
        
        # Return validated data
        return {
            "primary": validated_primary,
            "secondary": validated_secondary
        }
    
    def _validate_primary_data(self, primary_data):
        """Validate primary data (API sources)"""
        validated = {}
        
        for source_name, data in primary_data.items():
            # Check basic structure
            if not self._check_structure(data):
                self.logger.warning(f"Invalid structure in primary data from {source_name}")
                continue
            
            # Check data freshness
            if not self._check_freshness(data):
                self.logger.warning(f"Stale data from {source_name} - skipping")
                continue
            
            # Check for missing critical fields
            missing_fields = self._check_missing_fields(data, "primary")
            if missing_fields:
                self.logger.warning(f"Missing critical fields in data from {source_name}: {missing_fields}")
                continue
            
            # Check data quality
            if not self._check_data_quality(data):
                self.logger.warning(f"Data quality issues in data from {source_name}")
                continue
            
            validated[source_name] = data
        
        return validated
    
    def _validate_secondary_data(self, secondary_data):
        """Validate secondary data (scraped sources)"""
        validated = {}
        
        for source_name, data in secondary_data.items():
            # Check basic structure
            if not self._check_structure(data):
                self.logger.warning(f"Invalid structure in secondary data from {source_name}")
                continue
            
            # Check data freshness
            if not self._check_freshness(data):
                self.logger.warning(f"Stale data from {source_name} - skipping")
                continue
            
            # Check for missing critical fields
            missing_fields = self._check_missing_fields(data, "secondary")
            if missing_fields:
                self.logger.warning(f"Missing critical fields in data from {source_name}: {missing_fields}")
                continue
            
            # Check content quality
            if not self._check_content_quality(data):
                self.logger.warning(f"Insufficient content quality from {source_name}")
                continue
            
            validated[source_name] = data
        
        return validated
    
    def _check_structure(self, data):
        """Check if data has required structure"""
        required_keys = ["status", "timestamp", "data"]
        
        if not all(key in data for key in required_keys):
            return False
        
        if data["status"] != "success":
            return False
            
        return True
    
    def _check_freshness(self, data):
        """Check if data is fresh enough"""
        try:
            timestamp = datetime.fromisoformat(data["timestamp"])
            age = datetime.now() - timestamp
            return age < self.max_data_age
        except (KeyError, TypeError, ValueError):
            return False
    
    def _check_missing_fields(self, data, source_type):
        """Check for missing required fields"""
        missing_fields = []
        data_type = data.get("type", "default")
        
        # Get required fields for this data type
        required = self.required_fields[source_type].get(data_type, [])
        
        # Check for missing fields in data
        for field in required:
            if field not in data.get("data", {}):
                missing_fields.append(field)
        
        return missing_fields
    
    def _check_data_quality(self, data):
        """Check data quality metrics"""
        # In production, this would check for outliers, consistency, etc.
        return True
    
    def _check_content_quality(self, data):
        """Check quality of scraped content"""
        if "content" not in data:
            return False
        
        content = data["content"]
        
        # Minimum content length
        if len(content) < 200:
            return False
        
        # Must contain some meaningful text
        if not any(char.isalpha() for char in content):
            return False
        
        return True
    
    def _check_consistency(self, primary_data, secondary_data):
        """Check cross-source consistency"""
        # In production, this would compare key metrics across sources
        pass
