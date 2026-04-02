import logging
import asyncio
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler
from config.sources import MARKET_HOURS
from .formatter import TelegramFormatter

class TradingTelegramBot:
    """
    Telegram bot for the MarketPulse Trading Intelligence Platform.
    
    Handles:
    - User interactions and commands
    - Report delivery at scheduled times
    - User preference management
    - Interactive features (verification, conviction breakdown, etc.)
    """
    
    def __init__(self, token, agents):
        self.token = token
        self.agents = agents
        self.logger = logging.getLogger("TradingTelegramBot")
        self.formatter = TelegramFormatter()
        self.user_preferences = {}
        
        # Initialize Telegram application
        if token:
            self.application = Application.builder().token(token).build()
            self._register_handlers()
        else:
            self.application = None
    
    def _register_handlers(self):
        """Register all Telegram command handlers"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(CommandHandler("preferences", self.set_preferences))
        self.application.add_handler(CommandHandler("verify", self.verify_recommendation))
        self.application.add_handler(CommandHandler("conviction", self.show_conviction))
        self.application.add_handler(CommandHandler("history", self.show_history))
        self.application.add_handler(CommandHandler("portfolio", self.analyze_portfolio))
        self.application.add_handler(CommandHandler("schedule", self.show_schedule))
        self.application.add_handler(CommandHandler("trigger", self.trigger_report))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.unknown_command))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        welcome_message = (
            "👋 Welcome to MarketPulse Trading Intelligence!\n\n"
            "I deliver verified trading insights with source attribution and conviction scores for:\n"
            "• India (BSE/NSE)\n"
            "• US (NYSE/NASDAQ)\n"
            "• UK (LSE)\n"
            "• Singapore (SGX)\n\n"
            "You'll receive:\n"
            "⏰ Daily at 9:30 AM local time: Market outlook & intraday picks\n"
            "⏰ Daily at 3:45 PM local time: Market wrap-up & BTST recommendations\n"
            "📅 Every Sunday: Weekly market review\n\n"
            "Use /preferences to customize your experience\n"
            "Use /help for more information"
        )
        
        await update.message.reply_text(welcome_message)
        
        # Add user to preferences
        user_id = update.message.from_user.id
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {
                "countries": ["india", "us", "uk", "singapore"],
                "report_types": ["pre-market", "post-market", "weekend"],
                "detail_level": "medium",
                "timezone": "UTC"
            }
        
        # Store user ID for future reference
        self.logger.info(f"New user registered: {user_id}")
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = (
            "📚 MarketPulse Command Reference:\n\n"
            "/preferences - Customize your country and report preferences\n"
            "/verify [symbol] - Verify source and credibility of a recommendation\n"
            "/conviction [symbol] - See detailed conviction score breakdown\n"
            "/history [days] - View past recommendations and outcomes\n"
            "/portfolio - Upload and analyze your portfolio\n"
            "/schedule - Show your report delivery schedule\n"
            "/trigger [country] [report_type] - Manually trigger a report\n\n"
            "Your current preferences:\n"
            f"• Countries: {', '.join(self.user_preferences.get(update.message.from_user.id, {}).get('countries', []))}\n"
            f"• Report types: {', '.join(self.user_preferences.get(update.message.from_user.id, {}).get('report_types', []))}\n"
            f"• Detail level: {self.user_preferences.get(update.message.from_user.id, {}).get('detail_level', 'medium')}"
        )
        
        await update.message.reply_text(help_text)
    
    async def set_preferences(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /preferences command"""
        if not context.args:
            await update.message.reply_text(
                "🛠️ Current preferences:\n"
                "• Countries: india, us, uk, singapore\n"
                "• Report types: pre-market, post-market, weekend\n"
                "• Detail level: medium\n\n"
                "Use: /preferences [country1,country2] [report1,report2] [detail_level]\n"
                "Example: /preferences us,uk pre-market,post-market high"
            )
            return
        
        try:
            # Parse arguments
            args = " ".join(context.args).split()
            
            if len(args) < 3:
                await update.message.reply_text("❌ Please provide all three preference categories")
                return
            
            # Process countries
            countries = [c.strip().lower() for c in args[0].split(",")]
            valid_countries = ["india", "us", "uk", "singapore"]
            countries = [c for c in countries if c in valid_countries]
            
            # Process report types
            report_types = [r.strip().lower() for r in args[1].split(",")]
            valid_types = ["pre-market", "post-market", "weekend"]
            report_types = [r for r in report_types if r in valid_types]
            
            # Process detail level
            detail_level = args[2].lower()
            valid_levels = ["low", "medium", "high"]
            detail_level = detail_level if detail_level in valid_levels else "medium"
            
            # Update preferences
            user_id = update.message.from_user.id
            self.user_preferences[user_id] = {
                "countries": countries or ["india", "us", "uk", "singapore"],
                "report_types": report_types or ["pre-market", "post-market", "weekend"],
                "detail_level": detail_level,
                "timezone": self.user_preferences.get(user_id, {}).get("timezone", "UTC")
            }
            
            # Confirm changes
            await update.message.reply_text(
                "✅ Preferences updated!\n\n"
                f"• Countries: {', '.join(countries or ['All countries'])}\n"
                f"• Report types: {', '.join(report_types or ['All report types'])}\n"
                f"• Detail level: {detail_level}"
            )
            
        except Exception as e:
            self.logger.error(f"Error setting preferences: {str(e)}")
            await update.message.reply_text("❌ Error updating preferences. Please try again.")
    
    async def verify_recommendation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /verify command"""
        if not context.args:
            await update.message.reply_text("Please provide a stock symbol to verify (e.g., /verify RELIANCE)")
            return
        
        symbol = context.args[0].upper()
        
        # In a real implementation, this would check actual recommendation history
        verification_data = {
            "source": "NDTV Profit",
            "credibility": 0.75,
            "timestamp": "2023-11-15 09:29 AM IST",
            "status": "Intraday trade closed with +2.3% gain",
            "method": "Cross-referenced with Moneycontrol and Alpha Vantage data"
        }
        
        verification_message = self.formatter.format_verification(symbol, verification_data)
        await update.message.reply_text(verification_message)
    
    async def show_conviction(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /conviction command"""
        if not context.args:
            await update.message.reply_text("Please provide a stock symbol (e.g., /conviction RELIANCE)")
            return
        
        symbol = context.args[0].upper()
        
        # In a real implementation, this would check actual recommendation data
        breakdown_data = {
            "source_credibility": 0.75,
            "technical": {
                "momentum": 0.85,
                "volume_confirmation": 0.75,
                "support_resistance": 0.80
            },
            "risk_adjustment": -0.05,
            "conviction": 0.78,
            "recommendation": "Strong buy (intraday)"
        }
        
        conviction_message = self.formatter.format_conviction_breakdown(symbol, breakdown_data)
        await update.message.reply_text(conviction_message)
    
    async def show_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /history command"""
        days = 7  # Default
        if context.args:
            try:
                days = int(context.args[0])
            except ValueError:
                await update.message.reply_text("Please enter a valid number of days")
                return
        
        # In a real implementation, this would fetch actual history
        history_data = {
            "days": days,
            "total": 125,
            "win_rate": 0.68,
            "avg_gain": 2.45,
            "avg_loss": -1.25,
            "best_sector": "Banking",
            "best_sector_win_rate": 0.72,
            "worst_sector": "Energy",
            "worst_sector_win_rate": 0.58,
            "url": "marketpulse.example.com/history"
        }
        
        history_message = self.formatter.format_history(history_data)
        await update.message.reply_text(history_message)
    
    async def analyze_portfolio(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command"""
        await update.message.reply_text(
            "📊 Portfolio analysis is coming soon!\n"
            "Currently, you can upload your portfolio CSV file for analysis.\n\n"
            "Please send your portfolio file or use the web interface at:\n"
            "https://marketpulse.example.com/portfolio"
        )
    
    async def show_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /schedule command"""
        user_id = update.message.from_user.id
        preferences = self.user_preferences.get(user_id, {})
        
        schedule_text = "📅 Your Report Delivery Schedule:\n\n"
        
        for country in preferences.get("countries", ["india", "us", "uk", "singapore"]):
            market_hours = MARKET_HOURS.get(country, {})
            timezone = market_hours.get("timezone", "UTC")
            
            schedule_text += f"{self.formatter.color_coding.get(country, '')} {country.upper()} MARKET:\n"
            schedule_text += f"• Pre-market: 9:30 AM {timezone}\n"
            schedule_text += f"• Post-market: 3:45 PM {timezone}\n"
            schedule_text += f"• Weekend: Sunday 9:00 AM {timezone}\n\n"
        
        await update.message.reply_text(schedule_text)
    
    async def trigger_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /trigger command"""
        if len(context.args) < 2:
            await update.message.reply_text(
                "Usage: /trigger [country] [report_type]\n"
                "Example: /trigger india pre-market"
            )
            return
        
        country = context.args[0].lower()
        report_type = context.args[1].lower()
        
        valid_countries = ["india", "us", "uk", "singapore"]
        valid_types = ["pre-market", "post-market", "weekend"]
        
        if country not in valid_countries:
            await update.message.reply_text(f"Invalid country. Must be one of: {', '.join(valid_countries)}")
            return
        
        if report_type not in valid_types:
            await update.message.reply_text(f"Invalid report type. Must be one of: {', '.join(valid_types)}")
            return
        
        # In a real implementation, this would trigger the actual report generation
        await update.message.reply_text(
            f"🔄 Generating {report_type} report for {country}...\n\n"
            "This is a test command. In production, this would generate and send the report."
        )
    
    async def unknown_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle unknown commands"""
        await update.message.reply_text(
            "❌ Unknown command. Use /help to see available commands."
        )
    
    async def send_report(self, user_id, report_type, country, report):
        """Send a formatted report to a user"""
        if not report:
            self.logger.warning(f"Empty report for {country} {report_type}")
            return
        
        try:
            await self.application.bot.send_message(
                chat_id=user_id,
                text=report,
                parse_mode="Markdown"
            )
            self.logger.info(f"Sent {report_type} report for {country} to user {user_id}")
        except Exception as e:
            self.logger.error(f"Failed to send report to {user_id}: {str(e)}")
    
    async def start_polling(self):
        """Start the Telegram bot polling"""
        if not self.application:
            self.logger.error("Telegram bot cannot start without a token")
            return
        
        self.logger.info("Starting Telegram bot polling")
        
        # Start the bot
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()
        
        # Keep the bot running
        await asyncio.Event().wait()
    
    async def stop_polling(self):
        """Stop the Telegram bot polling"""
        self.logger.info("Stopping Telegram bot polling")
        
        if self.application:
            await self.application.updater.stop()
            await self.application.stop()
            await self.application.shutdown()
