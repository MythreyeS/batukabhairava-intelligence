# Data source configuration with reliability weights
DATA_SOURCES = {
    "india": {
        "primary": [
            {"name": "Finage", "api": "https://api.finage.co.uk", "weight": 0.9, "type": "api"},
            {"name": "AlphaVantage", "api": "https://www.alphavantage.co", "weight": 0.85, "type": "api"}
        ],
        "secondary": [
            {"name": "NDTV Profit", "url": "https://profit.ndtv.com", "weight": 0.75, "type": "scrape"},
            {"name": "Moneycontrol", "url": "https://www.moneycontrol.com", "weight": 0.7, "type": "scrape"}
        ]
    },
    "us": {
        "primary": [
            {"name": "Finnhub", "api": "https://finnhub.io", "weight": 0.92, "type": "api"},
            {"name": "AlphaVantage", "api": "https://www.alphavantage.co", "weight": 0.88, "type": "api"}
        ],
        "secondary": [
            {"name": "CNBC", "url": "https://www.cnbc.com", "weight": 0.78, "type": "scrape"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com", "weight": 0.75, "type": "scrape"}
        ]
    },
    "uk": {
        "primary": [
            {"name": "AlphaVantage", "api": "https://www.alphavantage.co", "weight": 0.88, "type": "api"},
            {"name": "FinancialTimes", "api": "https://api.ft.com", "weight": 0.85, "type": "api"}
        ],
        "secondary": [
            {"name": "CityAM", "url": "https://www.cityam.com", "weight": 0.7, "type": "scrape"},
            {"name": "Reuters", "url": "https://www.reuters.com", "weight": 0.75, "type": "scrape"}
        ]
    },
    "singapore": {
        "primary": [
            {"name": "iTick", "api": "https://api.itick.org", "weight": 0.9, "type": "api"},
            {"name": "AlphaVantage", "api": "https://www.alphavantage.co", "weight": 0.85, "type": "api"}
        ],
        "secondary": [
            {"name": "TheEdgeSingapore", "url": "https://www.theedgesingapore.com", "weight": 0.75, "type": "scrape"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com", "weight": 0.7, "type": "scrape"}
        ]
    }
}

# Country-specific market hours (in local time)
MARKET_HOURS = {
    "india": {
        "open": "09:15",
        "close": "15:30",
        "timezone": "Asia/Kolkata"
    },
    "us": {
        "open": "09:30",
        "close": "16:00",
        "timezone": "America/New_York"
    },
    "uk": {
        "open": "08:00",
        "close": "16:30",
        "timezone": "Europe/London"
    },
    "singapore": {
        "open": "09:00",
        "close": "17:00",
        "timezone": "Asia/Singapore"
    }
}
