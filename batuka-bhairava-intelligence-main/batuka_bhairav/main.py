import logging
import os
import asyncio
import sys
from datetime import datetime
import pytz
from agents import initialize_agents
from telegram import initialize_telegram_integration
from config import initialize_configuration

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler("marketpulse.log"),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("MarketPulse")

async def main():
    """Main entry point for the MarketPulse Trading Intelligence Platform"""
    logger.info("Starting MarketPulse Trading Intelligence Platform")
    
    # Initialize configuration
    try:
        config = initialize_configuration()
        logger.info("Configuration initialized successfully")
    except Exception as e:
        logger.error(f"Configuration initialization failed: {str(e)}")
        sys.exit(1)
    
    # Initialize agents
    try:
        agents = initialize_agents()
        logger.info("Trading agents initialized successfully")
    except Exception as e:
        logger.error(f"Agents initialization failed: {str(e)}")
        sys.exit(1)
    
    # Initialize Telegram integration
    try:
        # Get Telegram token from environment
        telegram_token = os.getenv("TELEGRAM_TOKEN")
        if not telegram_token:
            logger.error("TELEGRAM_TOKEN environment variable not set")
            sys.exit(1)
        
        bot, scheduler = initialize_telegram_integration(agents)
        bot.token = telegram_token
        logger.info("Telegram integration initialized successfully")
    except Exception as e:
        logger.error(f"Telegram initialization failed: {str(e)}")
        sys.exit(1)
    
    # Start the Telegram bot
    logger.info("Starting Telegram bot polling")
    await bot.start_polling()

if __name__ == "__main__":
    # Check if required environment variables are set
    if not os.getenv("TELEGRAM_TOKEN"):
        logger.error("TELEGRAM_TOKEN environment variable is required")
        logger.error("Set it using: export TELEGRAM_TOKEN='your_token_here'")
        sys.exit(1)
    
    # Check if we're running in the correct environment
    if sys.version_info < (3, 8):
        logger.error("Python 3.8+ is required")
        sys.exit(1)
    
    try:
        # Run the main application
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.exception(f"Application crashed: {str(e)}")
        sys.exit(1)
