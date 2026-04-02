from .base_agent import BaseAgent
import logging
from datetime import datetime, timedelta

class UKAgent(BaseAgent):
    def __init__(self):
        super().__init__("uk")
        self.logger = logging.getLogger("UK Agent")
    
    def _format_pre_market_report(self):
        """Format UK pre-market report for Telegram"""
        if not self.recommendations:
            return None
        
        # Get market summary data
        market_data = self.processed_data.get("market_summary", {})
        ftse_data = market_data.get("ftse100", {})
        
        # Create formatted report
        report = f"🇬🇧 UK MARKET OUTLOOK - {datetime.now().strftime('%d %b %Y')}\n\n"
        
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
        """Format UK post-market report for Telegram"""
        if not self.recommendations:
            return None
        
        # Get market summary data
        market_data = self.processed_data.get("market_summary", {})
        ftse_data = market_data.get("ftse100", {})
        
        # Create formatted report
        report = f"🇬🇧 UK MARKET WRAP - {datetime.now().strftime('%d %b %Y')}\n\n"
        
        # Final index
        if ftse_data:
            report += f"📊 FINAL INDEX: FTSE 100 {ftse_data['value']:.2f} ({ftse_data['change_percent']:.2f}%)\n"
        
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
        """Analyze UK market trend for prediction"""
        # This would use actual analysis in production
        return {
            "trend": "neutral",
            "confidence": 0.68,
            "key_driver": "Stable GBP at $1.2750 with no major economic data releases today"
        }
    
    def _get_top_sectors(self):
        """Get top performing sectors in UK market"""
        # In production, this would use processed sector data
        return [
            {"name": "Financials", "weight": 0.22, "change": 0.75},
            {"name": "Energy", "weight": 0.18, "change": 0.6},
            {"name": "Industrials", "weight": 0.15, "change": 0.45}
        ]
    
    def _get_man_of_match(self):
        """Identify man of the match stock in UK market"""
        # In production, this would find the best performing stock
        return {
            "symbol": "HSBA.L",
            "name": "HSBC Holdings",
            "change": 3.2
        }
    
    def _generate_risk_note(self):
        """Generate risk note for UK market report"""
        # In production, this would analyze current risk factors
        return "UK CPI data release tomorrow may cause volatility"
    
    def _get_sector_deep_dive(self):
        """Generate sector deep dive content for UK market"""
        # In production, this would provide detailed sector analysis
        return "Financials sector outperformed due to stronger-than-expected banking sector results and improved lending metrics"
