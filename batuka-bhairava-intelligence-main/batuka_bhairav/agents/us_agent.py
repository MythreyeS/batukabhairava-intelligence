from .base_agent import BaseAgent
import logging
from datetime import datetime, timedelta

class USAgent(BaseAgent):
    def __init__(self):
        super().__init__("us")
        self.logger = logging.getLogger("US Agent")
    
    def _format_pre_market_report(self):
        """Format US pre-market report for Telegram"""
        if not self.recommendations:
            return None
        
        # Get market summary data
        market_data = self.processed_data.get("market_summary", {})
        sp500_data = market_data.get("sp500", {})
        
        # Create formatted report
        report = f"🇺🇸 US MARKET OUTLOOK - {datetime.now().strftime('%d %b %Y')}\n\n"
        
        # Market prediction
        prediction = self._analyze_market_trend()
        report += f"🎯 PREDICTION: {prediction['trend'].title()} ({prediction['confidence']*100:.0f}% confidence)\n"
        
        # Key driver
        report += f"📈 KEY DRIVER: {prediction['key_driver']}\n\n"
        
        # Top sectors
        sectors = self._get_top_sectors()
        report += "🔥 TOP 3 SECTORS:\n"
        for i, sector in enumerate(sectors[:3], 1):
            report += f"   {i}. {sector['name']} ({sector['weight']*100:.0f}% weight)\n"
        
        # Recommendations
        report += "\n💡 INTRADAY PICKS ({count}):\n".format(count=min(15, len(self.recommendations)))
        for rec in self.recommendations[:15]:
            report += f"   - {rec['symbol']} | {rec['conviction']*100:.0f}% conviction | Source: {rec['source']}\n"
            report += f"     Entry: {rec['entry_zone']} | Target: {rec['target']} | SL: {rec['stop_loss']}\n"
        
        # Risk note
        risk_note = self._generate_risk_note()
        report += f"\n⚠️ RISK NOTE: {risk_note}"
        
        return report
    
    def _format_post_market_report(self):
        """Format US post-market report for Telegram"""
        if not self.recommendations:
            return None
        
        # Get market summary data
        market_data = self.processed_data.get("market_summary", {})
        sp500_data = market_data.get("sp500", {})
        
        # Create formatted report
        report = f"🇺🇸 US MARKET WRAP - {datetime.now().strftime('%d %b %Y')}\n\n"
        
        # Final index
        if sp500_data:
            report += f"📊 FINAL INDEX: S&P 500 {sp500_data['value']:.2f} ({sp500_data['change_percent']:.2f}%)\n"
        
        # Man of the match
        mom = self._get_man_of_match()
        if mom:
            report += f"🏆 MAN OF THE MATCH: {mom['symbol']} ({mom['name']}) +{mom['change']:.2f}%\n"
        
        # Top sectors
        sectors = self._get_top_sectors()
        report += "\n📈 TOP PERFORMING SECTORS:\n"
        for i, sector in enumerate(sectors[:3], 1):
            report += f"   {i}. {sector['name']} (+{sector['change']:.2f}%)\n"
        
        # BTST recommendations
        btst_recs = [rec for rec in self.recommendations if rec['timeframe'] == 'btst']
        report += f"\n💡 BTST RECOMMENDATIONS ({min(15, len(btst_recs))}):\n"
        for rec in btst_recs[:15]:
            report += f"   - {rec['symbol']} | Target: {rec['target']:.2f} | SL: {rec['stop_loss']:.2f}\n"
        
        # Sector deep dive
        sector_dive = self._get_sector_deep_dive()
        report += f"\n🔍 SECTOR DEEP DIVE: {sector_dive}"
        
        return report
    
    def _analyze_market_trend(self):
        """Analyze US market trend for prediction"""
        # This would use actual analysis in production
        return {
            "trend": "bullish",
            "confidence": 0.72,
            "key_driver": "Positive earnings season with 75% of S&P 500 companies beating estimates"
        }
    
    def _get_top_sectors(self):
        """Get top performing sectors in US market"""
        # In production, this would use processed sector data
        return [
            {"name": "Technology", "weight": 0.28, "change": 1.5},
            {"name": "Consumer Discretionary", "weight": 0.15, "change": 1.2},
            {"name": "Healthcare", "weight": 0.14, "change": 0.85}
        ]
    
    def _get_man_of_match(self):
        """Identify man of the match stock in US market"""
        # In production, this would find the best performing stock
        return {
            "symbol": "NVDA",
            "name": "NVIDIA Corporation",
            "change": 5.75
        }
    
    def _generate_risk_note(self):
        """Generate risk note for US market report"""
        # In production, this would analyze current risk factors
        return "Federal Reserve rate decision announcement expected at 2 PM EST"
    
    def _get_sector_deep_dive(self):
        """Generate sector deep dive content for US market"""
        # In production, this would provide detailed sector analysis
        return "Technology sector outperformed due to strong AI infrastructure investment and data center expansion announcements"
