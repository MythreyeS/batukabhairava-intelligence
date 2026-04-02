import logging
import asyncio
from datetime import datetime, time, timedelta
import pytz
from config.sources import MARKET_HOURS

class ReportScheduler:
    """
    Schedules and coordinates the generation and delivery of market reports.
    
    Manages timing for all report types across all countries, ensuring reports
    are generated just before delivery time and sent at the exact scheduled time.
    """
    
    def __init__(self, agents):
        self.agents = agents
        self.logger = logging.getLogger("ReportScheduler")
        
        # Schedule configuration
        self.schedule = self._create_schedule()
        
        # Initialize state
        self.active = False
        self.scheduled_tasks = {}
    
    def _create_schedule(self):
        """Create the report schedule based on market hours"""
        schedule = {}
        
        for country, config in MARKET_HOURS.items():
            # Pre-market report (30 minutes before market open)
            pre_market_time = self._calculate_schedule_time(
                config["open"], 
                timedelta(minutes=-30)
            )
            
            # Post-market report (15 minutes before market close)
            post_market_time = self._calculate_schedule_time(
                config["close"], 
                timedelta(minutes=-15)
            )
            
            # Weekend report (Sunday morning)
            weekend_time = time(9, 0)
            
            schedule[country] = {
                "pre_market": pre_market_time,
                "post_market": post_market_time,
                "weekend": weekend_time
            }
        
        return schedule
    
    def _calculate_schedule_time(self, time_str, adjustment):
        """Calculate schedule time with adjustment"""
        h, m = map(int, time_str.split(':'))
        base_time = time(h, m)
        
        # Convert to datetime for calculation
        now = datetime.now()
        base_datetime = datetime(now.year, now.month, now.day, h, m)
        adjusted = base_datetime + adjustment
        
        return time(adjusted.hour, adjusted.minute)
    
    def _get_next_report_time(self, country, report_type):
        """Get the next scheduled time for a report"""
        now = datetime.now(pytz.timezone(MARKET_HOURS[country]["timezone"]))
        schedule_time = self.schedule[country][report_type]
        
        # Create datetime for schedule time today
        today_time = datetime(now.year, now.month, now.day, 
                             schedule_time.hour, schedule_time.minute, tzinfo=now.tzinfo)
        
        # If already past today's time, schedule for tomorrow
        if now > today_time:
            tomorrow = now + timedelta(days=1)
            next_time = datetime(tomorrow.year, tomorrow.month, tomorrow.day,
                                schedule_time.hour, schedule_time.minute, tzinfo=now.tzinfo)
        else:
            next_time = today_time
        
        return next_time
    
    async def start_scheduling(self):
        """Start the scheduling process"""
        self.logger.info("Starting report scheduling")
        self.active = True
        
        # Schedule all reports
        for country in self.agents.keys():
            await self._schedule_country_reports(country)
        
        # Run continuously
        while self.active:
            await asyncio.sleep(60)  # Check every minute
    
    async def _schedule_country_reports(self, country):
        """Schedule all report types for a country"""
        # Pre-market report
        await self._schedule_report(country, "pre_market")
        
        # Post-market report
        await self._schedule_report(country, "post_market")
        
        # Weekend report (only for Sunday)
        await self._schedule_report(country, "weekend")
    
    async def _schedule_report(self, country, report_type):
        """Schedule a specific report type for a country"""
        next_time = self._get_next_report_time(country, report_type)
        
        # Calculate time to wait
        wait_seconds = (next_time - datetime.now(next_time.tzinfo)).total_seconds()
        
        # Store task
        task_name = f"{country}_{report_type}"
        if task_name in self.scheduled_tasks:
            self.scheduled_tasks[task_name].cancel()
        
        # Schedule the task
        self.scheduled_tasks[task_name] = asyncio.create_task(
            self._wait_and_generate_report(country, report_type, wait_seconds)
        )
        
        self.logger.info(
            f"Scheduled {report_type} report for {country} at "
            f"{next_time.strftime('%Y-%m-%d %H:%M %Z')}"
        )
    
    async def _wait_and_generate_report(self, country, report_type, wait_seconds):
        """Wait for scheduled time and generate the report"""
        if wait_seconds > 0:
            await asyncio.sleep(wait_seconds)
        
        self.logger.info(f"Generating {report_type} report for {country}")
        
        # Generate report
        report = await self._generate_report(country, report_type)
        
        # Schedule next occurrence
        await self._schedule_report(country, report_type)
        
        return report
    
    async def _generate_report(self, country, report_type):
        """Generate a report for a country and report type"""
        agent = self.agents[country]
        
        # Check if it's time to run
        if not agent.is_time_to_run(report_type):
            self.logger.warning(f"Not time to run {report_type} report for {country}")
            return None
        
        # Run the agent
        report_data = agent.run(report_type)
        
        # Format the report
        formatted_report = agent.format_report(report_type)
        
        # Here you would typically send the report to the bot for delivery
        # In a real implementation, you'd return the formatted report to be sent
        
        self.logger.info(f"Generated {report_type} report for {country}")
        return formatted_report
    
    def stop_scheduling(self):
        """Stop the scheduling process"""
        self.logger.info("Stopping report scheduling")
        self.active = False
        
        # Cancel all scheduled tasks
        for task in self.scheduled_tasks.values():
            task.cancel()
        
        self.scheduled_tasks = {}
    
    def get_schedule_status(self):
        """Get current schedule status"""
        status = {}
        
        for country, times in self.schedule.items():
            status[country] = {}
            for report_type, time_obj in times.items():
                next_time = self._get_next_report_time(country, report_type)
                status[country][report_type] = next_time.strftime("%Y-%m-%d %H:%M %Z")
        
        return status
    
    def get_next_report_time(self, country, report_type):
        """Get the next scheduled time for a report"""
        return self._get_next_report_time(country, report_type)
    
    async def trigger_report(self, country, report_type):
        """
        Manually trigger a report generation
        
        Args:
            country (str): Country code
            report_type (str): Report type
            
        Returns:
            dict: Report data
        """
        self.logger.info(f"Manually triggering {report_type} report for {country}")
        
        # Cancel existing schedule if it exists
        task_name = f"{country}_{report_type}"
        if task_name in self.scheduled_tasks:
            self.scheduled_tasks[task_name].cancel()
            del self.scheduled_tasks[task_name]
        
        # Generate the report immediately
        return await self._generate_report(country, report_type)
