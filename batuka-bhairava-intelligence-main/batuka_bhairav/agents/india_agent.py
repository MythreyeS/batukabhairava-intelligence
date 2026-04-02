from .base_agent import BaseAgent
import logging
from datetime import datetime, timedelta

class IndiaAgent(BaseAgent):
    def __init__(self):
        super().__init__("india")
        self.logger = logging.getLogger("India Agent")
    
    def _format_pre_market_report(self):
        """Format India pre-market report for Telegram"""
        if not self.recommendations:
            return None
        
        # Get market summary data
        market_data = self.processed_data.get("market_summary", {})
        nifty_data = market_data.get("nifty50", {})
        
        # Create formatted report
        report = f"🇮🇳 INDIAN MARKET OUTLOOK - {datetime.now().strftime('%d %b %Y')}\n\n"
        
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
        """Format India post-market report for Telegram"""
        if not self.recommendations:
            return None
        
        # Get market summary data
        market_data = self.processed_data.get("market_summary", {})
        nifty_data = market_data.get("nifty50", {})
        
        # Create formatted report
        report = f"🇮🇳 INDIAN MARKET WRAP - {datetime.now().strftime('%d %b %Y')}\n\n"
        
        # Final index
        if nifty_data:
            report += f"📊 FINAL INDEX: Nifty 50 {nifty_data['value']:.2f} ({nifty_data['change_percent']:.2f}%)\n"
        
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
        """Analyze market trend for prediction"""
        # This would use actual analysis in production
        return {
            "trend": "bullish",
            "confidence": 0.78,
            "key_driver": "FII buying resurgence (INR 1,250cr net inflow yesterday)"
        }
    
    def _get_top_sectors(self):
        """Get top performing sectors"""
        # In production, this would use processed sector data
        return [
            {"name": "Banking", "weight": 0.22, "change": 1.25},
            {"name": "Auto", "weight": 0.18, "change": 0.95},
            {"name": "Energy", "weight": 0.15, "change": 1.4}
        ]
    
    def _get_man_of_match(self):
        """Identify man of the match stock"""
        # In production, this would find the best performing stock
        return {
            "symbol": "RELIANCE",
            "name": "Reliance Industries",
            "change": 4.25
        }
    
    def _generate_risk_note(self):
        """Generate risk note for the report"""
        # In production, this would analyze current risk factors
        return "US CPI data release today may cause volatility after 10:30 AM"
    
    def _get_sector_deep_dive(self):
        """Generate sector deep dive content"""
        # In production, this would provide detailed sector analysis
        return "Banking sector outperformed due to strong Q3 results and improved loan growth prospects"
