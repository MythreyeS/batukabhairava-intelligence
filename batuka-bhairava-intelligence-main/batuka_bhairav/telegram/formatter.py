import logging
from datetime import datetime, timedelta
import pytz
from config.sources import MARKET_HOURS

class TelegramFormatter:
    """
    Formats market data and recommendations into Telegram-friendly messages.
    
    Handles different report types (pre-market, post-market, weekend) for all countries
    with appropriate formatting, emojis, and structure for optimal Telegram delivery.
    """
    
    def __init__(self):
        self.logger = logging.getLogger("TelegramFormatter")
        self.color_coding = {
            "india": "🇮🇳",
            "us": "🇺🇸",
            "uk": "🇬🇧",
            "singapore": "🇸🇬"
        }
    
    def format_report(self, country, report_type, data):
        """
        Format a report for Telegram delivery
        
        Args:
            country (str): Country code (india, us, uk, singapore)
            report_type (str): Type of report (pre-market, post-market, weekend)
            data (dict): Report data to format
            
        Returns:
            str: Formatted message ready for Telegram
        """
        if report_type == "pre-market":
            return self._format_pre_market_report(country, data)
        elif report_type == "post-market":
            return self._format_post_market_report(country, data)
        elif report_type == "weekend":
            return self._format_weekend_report(country, data)
        else:
            self.logger.error(f"Invalid report type: {report_type}")
            return None
    
    def _format_pre_market_report(self, country, data):
        """Format pre-market report for Telegram"""
        if not data.get("recommendations"):
            self.logger.warning(f"No recommendations for {country} pre-market report")
            return None
        
        # Get market data
        market_data = data.get("market_data", {})
        index_data = market_data.get("index", {})
        
        # Create formatted report
        country_flag = self.color_coding.get(country, "")
        report = f"{country_flag} {country.upper()} MARKET OUTLOOK - {datetime.now().strftime('%d %b %Y')}\n\n"
        
        # Market prediction
        prediction = data.get("prediction", {})
        report += f"🎯 PREDICTION: {prediction.get('trend', 'Neutral').title()} ({prediction.get('confidence', 0.5)*100:.0f}% confidence)\n"
        
        # Key driver
        report += f"📈 KEY DRIVER: {prediction.get('key_driver', 'No key driver identified')}\n\n"
        
        # Top sectors
        sectors = data.get("sectors", [])
        report += "🔥 TOP 3 SECTORS:\n"
        for i, sector in enumerate(sectors[:3], 1):
            report += f"   {i}. {sector['name']} ({sector['weight']*100:.0f}% weight)\n"
        
        # Recommendations
        recommendations = data.get("recommendations", [])
        report += f"\n💡 INTRADAY PICKS ({min(15, len(recommendations))}):\n"
        for rec in recommendations[:15]:
            report += f"   - {rec['symbol']} | {rec['conviction']*100:.0f}% conviction | Source: {rec['source']}\n"
            report += f"     Entry: {rec['entry_zone']} | Target: {rec['target']:.2f} | SL: {rec['stop_loss']:.2f}\n"
        
        # Risk note
        risk_note = data.get("risk_note", "No significant risks identified")
        report += f"\n⚠️ RISK NOTE: {risk_note}"
        
        return report
    
    def _format_post_market_report(self, country, data):
        """Format post-market report for Telegram"""
        if not data.get("recommendations"):
            self.logger.warning(f"No recommendations for {country} post-market report")
            return None
        
        # Get market data
        market_data = data.get("market_data", {})
        index_data = market_data.get("index", {})
        
        # Create formatted report
        country_flag = self.color_coding.get(country, "")
        report = f"{country_flag} {country.upper()} MARKET WRAP - {datetime.now().strftime('%d %b %Y')}\n\n"
        
        # Final index
        if index_data:
            report += f"📊 FINAL INDEX: {index_data.get('name', 'Benchmark')} {index_data.get('value', 0):.2f} ({index_data.get('change_percent', 0):.2f}%)\n"
        
        # Man of the match
        mom = data.get("man_of_match", {})
        if mom:
            report += f"🏆 MAN OF THE MATCH: {mom.get('symbol', 'N/A')} ({mom.get('name', 'N/A')}) +{mom.get('change', 0):.2f}%\n"
        
        # Top sectors
        sectors = data.get("sectors", [])
        report += "\n📈 TOP PERFORMING SECTORS:\n"
        for i, sector in enumerate(sectors[:3], 1):
            report += f"   {i}. {sector['name']} (+{sector['change']:.2f}%)\n"
        
        # BTST recommendations
        btst_recs = [rec for rec in data.get("recommendations", []) if rec.get("timeframe") == 'btst']
        report += f"\n💡 BTST RECOMMENDATIONS ({min(15, len(btst_recs))}):\n"
        for rec in btst_recs[:15]:
            report += f"   - {rec['symbol']} | Target: {rec['target']:.2f} | SL: {rec['stop_loss']:.2f}\n"
        
        # Sector deep dive
        sector_dive = data.get("sector_deep_dive", "No sector deep dive available")
        report += f"\n🔍 SECTOR DEEP DIVE: {sector_dive}"
        
        return report
    
    def _format_weekend_report(self, country, data):
        """Format weekend report for Telegram"""
        # Get weekly data
        weekly_data = data.get("weekly_data", {})
        market_data = weekly_data.get("market_data", {})
        index_data = market_data.get("index", {})
        
        # Create formatted report
        country_flag = self.color_coding.get(country, "")
        report = f"{country_flag} {country.upper()} WEEKLY REVIEW - {datetime.now().strftime('%d %b %Y')}\n\n"
        
        # Weekly performance
        if index_data:
            report += f"📊 WEEKLY PERFORMANCE: {index_data.get('name', 'Benchmark')} {index_data.get('value', 0):.2f} ({index_data.get('change_percent', 0):.2f}%)\n\n"
        
        # Top performers
        top_performers = weekly_data.get("top_performers", [])
        report += "🏆 TOP 5 PERFORMERS:\n"
        for i, stock in enumerate(top_performers[:5], 1):
            report += f"   {i}. {stock['symbol']} ({stock['name']}) +{stock['change']:.2f}%\n"
        
        # Sector performance
        sectors = weekly_data.get("sector_performance", [])
        report += "\n📈 SECTOR PERFORMANCE:\n"
        for i, sector in enumerate(sectors[:3], 1):
            report += f"   {i}. {sector['name']} (+{sector['change']:.2f}%)\n"
        
        # Portfolio analysis
        portfolio = data.get("portfolio", {})
        if portfolio:
            report += f"\n📊 YOUR PORTFOLIO:\n"
            report += f"• Total Value: {portfolio.get('value', 'N/A')}\n"
            report += f"• Weekly Change: {portfolio.get('change_percent', 0):.2f}%\n"
            report += f"• Top Holding: {portfolio.get('top_holding', 'N/A')}\n"
        
        # Market outlook
        outlook = data.get("outlook", "No market outlook available")
        report += f"\n🔍 NEXT WEEK OUTLOOK: {outlook}"
        
        return report
    
    def format_verification(self, symbol, verification_data):
        """
        Format verification details for a recommendation
        
        Args:
            symbol (str): Stock symbol
            verification_data (dict): Verification information
            
        Returns:
            str: Formatted verification message
        """
        return (
            f"🔍 Verification for {symbol}:\n\n"
            f"• Source: {verification_data.get('source', 'N/A')}\n"
            f"• Credibility Score: {verification_data.get('credibility', 0)*100:.0f}%\n"
            f"• Time of Recommendation: {verification_data.get('timestamp', 'N/A')}\n"
            f"• Current Status: {verification_data.get('status', 'N/A')}\n"
            f"• Verification Method: {verification_data.get('method', 'N/A')}"
        )
    
    def format_conviction_breakdown(self, symbol, breakdown_data):
        """
        Format conviction score breakdown
        
        Args:
            symbol (str): Stock symbol
            breakdown_data (dict): Conviction breakdown data
            
        Returns:
            str: Formatted conviction breakdown
        """
        # Format technical analysis
        technical = breakdown_data.get("technical", {})
        technical_str = "\n".join([
            f"  - {k.replace('_', ' ').title()}: {v*100:.0f}%" 
            for k, v in technical.items()
        ])
        
        return (
            f"📊 {symbol} Conviction Breakdown:\n\n"
            f"• Source Credibility: {breakdown_data.get('source_credibility', 0)*100:.0f}%\n"
            f"• Technical Analysis:\n{technical_str}\n"
            f"• Risk Adjustment: {breakdown_data.get('risk_adjustment', 0)*100:+.0f}%\n\n"
            f"✅ Final Conviction Score: {breakdown_data.get('conviction', 0)*100:.0f}%\n"
            f"💡 Recommendation: {breakdown_data.get('recommendation', 'N/A')}"
        )
    
    def format_history(self, history_data):
        """
        Format historical recommendation performance
        
        Args:
            history_data (dict): Historical performance data
            
        Returns:
            str: Formatted history message
        """
        # Calculate win rate
        win_rate = history_data.get("win_rate", 0)
        
        return (
            f"📈 Recommendation History ({history_data.get('days', 7)} Days):\n\n"
            f"• Total recommendations: {history_data.get('total', 0)}\n"
            f"• Win rate: {win_rate*100:.0f}%\n"
            f"• Average gain on winning trades: +{history_data.get('avg_gain', 0):.2f}%\n"
            f"• Average loss on losing trades: {history_data.get('avg_loss', 0):.2f}%\n"
            f"• Best performing sector: {history_data.get('best_sector', 'N/A')} ({history_data.get('best_sector_win_rate', 0)*100:.0f}%)\n"
            f"• Worst performing sector: {history_data.get('worst_sector', 'N/A')} ({history_data.get('worst_sector_win_rate', 0)*100:.0f}%)\n\n"
            f"See full history at: {history_data.get('url', 'N/A')}"
        )
    
    def format_portfolio_analysis(self, portfolio_data):
        """
        Format portfolio analysis
        
        Args:
            portfolio_data (dict): Portfolio data
            
        Returns:
            str: Formatted portfolio analysis
        """
        # Format holdings
        holdings_str = "\n".join([
            f"• {h['symbol']}: {h['change']:+.2f}% ({h['weight']*100:.0f}%)"
            for h in portfolio_data.get("holdings", [])[:5]
        ])
        
        return (
            f"📊 Portfolio Analysis:\n\n"
            f"• Total Value: {portfolio_data.get('value', 'N/A')}\n"
            f"• Overall Performance: {portfolio_data.get('change_percent', 0):+.2f}%\n"
            f"• Number of Holdings: {portfolio_data.get('num_holdings', 0)}\n\n"
            f"Top Holdings:\n{holdings_str}\n\n"
            f"💡 Suggested Actions:\n"
            f"• {portfolio_data.get('suggestions', ['No suggestions available'])[0]}\n"
            f"• {portfolio_data.get('suggestions', ['No suggestions available'])[1]}"
        )
