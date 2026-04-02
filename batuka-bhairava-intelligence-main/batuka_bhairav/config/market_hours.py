import logging
from datetime import time

# Configure logging
logger = logging.getLogger("MarketHoursConfig")

# Market hours configuration for all countries
MARKET_HOURS = {
    "india": {
        "open": "09:15",
        "close": "15:30",
        "timezone": "Asia/Kolkata",
        "pre_market": "09:00",
        "post_market": "15:45",
        "lunch_break": {"start": "12:00", "end": "12:30"},
        "holidays": []
    },
    "us": {
        "open": "09:30",
        "close": "16:00",
        "timezone": "America/New_York",
        "pre_market": "08:00",
        "post_market": "16:15",
        "lunch_break": None,
        "holidays": []
    },
    "uk": {
        "open": "08:00",
        "close": "16:30",
        "timezone": "Europe/London",
        "pre_market": "07:00",
        "post_market": "16:45",
        "lunch_break": None,
        "holidays": []
    },
    "singapore": {
        "open": "09:00",
        "close": "17:00",
        "timezone": "Asia/Singapore",
        "pre_market": "08:30",
        "post_market": "17:15",
        "lunch_break": {"start": "12:00", "end": "13:00"},
        "holidays": []
    }
}

def get_market_hours(country_code):
    """
    Get market hours for a specific country
    
    Args:
        country_code (str): Country code (india, us, uk, singapore)
        
    Returns:
        dict: Market hours configuration for the country
    """
    if country_code not in MARKET_HOURS:
        logger.error(f"Invalid country code: {country_code}")
        return None
    
    return MARKET_HOURS[country_code]

def is_market_open(country_code, current_time=None):
    """
    Check if the market is open for a specific country
    
    Args:
        country_code (str): Country code
        current_time (datetime, optional): Time to check (defaults to now)
        
    Returns:
        bool: True if market is open
    """
    if country_code not in MARKET_HOURS:
        return False
    
    from datetime import datetime
    import pytz
    
    if current_time is None:
        current_time = datetime.now(pytz.timezone(MARKET_HOURS[country_code]["timezone"]))
    
    # Parse market hours
    open_time = datetime.strptime(MARKET_HOURS[country_code]["open"], "%H:%M").time()
    close_time = datetime.strptime(MARKET_HOURS[country_code]["close"], "%H:%M").time()
    
    # Check if within market hours
    is_open = open_time <= current_time.time() <= close_time
    
    # Handle lunch break (if applicable)
    lunch_break = MARKET_HOURS[country_code]["lunch_break"]
    if lunch_break and is_open:
        lunch_start = datetime.strptime(lunch_break["start"], "%H:%M").time()
        lunch_end = datetime.strptime(lunch_break["end"], "%H:%M").time()
        is_open = not (lunch_start <= current_time.time() <= lunch_end)
    
    return is_open
