from .base_agent import BaseAgent
import logging
from datetime import datetime, timedelta

class SingaporeAgent(BaseAgent):
    def __init__(self):
        super().__init__("singapore")
        self.logger = logging.getLogger("Singapore Agent")
    
    def _format_pre_market_report(self):
        """Format Singapore pre-market report for Telegram"""
        if not self.recommendations:
            return None
        
        # Get market summary data
        market_data = self.processed_data.get("market_summary", {})
        sti_data = market_data.get("sti", {})
        
        # Create formatted report
        report = f"🇸🇬 SINGAPORE MARKET OUTLOOK - {datetime.now().strftime('%d %b %Y')}\n\n"
        
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
        """Format Singapore post-market report for Telegram"""
        if not self.recommendations:
            return None
        
        # Get market summary data
        market_data = self.processed_data.get("market_summary", {})
        sti_data = market_data.get("sti", {})
        
        # Create formatted report
        report = f"🇸🇬 SINGAPORE MARKET WRAP - {datetime.now().strftime('%d %b %Y')}\n\n"
        
        # Final index
        if sti_data:
            report += f"📊 FINAL INDEX: STI {sti_data['value']:.2f} ({sti_data['change_percent']:.2f}%)\n"
        
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
        """Analyze Singapore market trend for prediction"""
        # This would use actual analysis in production
        return {
            "trend": "bullish",
            "confidence": 0.75,
            "key_driver": "Strong inflow of foreign capital into Singapore REITs and banking sector"
        }
    
    def _get_top_sectors(self):
        """Get top performing sectors in Singapore market"""
        # In production, this would use processed sector data
        return [
            {"name": "REITs", "weight": 0.25, "change": 1.8},
            {"name": "Banks", "weight": 0.20, "change": 1.5},
            {"name": "Technology", "weight": 0.15, "change": 1.2}
        ]
    
    def _get_man_of_match(self):
        """Identify man of the match stock in Singapore market"""
        # In production, this would find the best performing stock
        return {
            "symbol": "C31.SI",
            "name": "CapitaLand Group",
            "change": 4.1
        }
    
    def _generate_risk_note(self):
        """Generate risk note for Singapore market report"""
        # In production, this would analyze current risk factors
        return "Global tech sector volatility may impact Singapore's technology stocks"
    
    def _get_sector_deep_dive(self):
        """Generate sector deep dive content for Singapore market"""
        # In production, this would provide detailed sector analysis
        return "REIT sector outperformed due to strong Q3 results and yield advantage over government bonds"
