from datetime import datetime, timedelta
from airflow.plugins_manager import AirflowPlugin
from airflow.timetables.base import Timetable


class TuesdayThursdayTimetable(Timetable):
    """Runs every Tuesday and Thursday at 2 PM"""
    
    def next_dagrun_info(self, last_automated_dagrun, restriction):
        if last_automated_dagrun is None:
            # First run - find next Tuesday or Thursday at 2 PM
            start_date = restriction.earliest
        else:
            # Find next Tuesday or Thursday after last run
            start_date = last_automated_dagrun.execution_date + timedelta(days=1)
        
        # Find next Tuesday (1) or Thursday (3)
        while start_date.weekday() not in [1, 3]:  # 1=Tuesday, 3=Thursday
            start_date += timedelta(days=1)
        
        # Set to 2 PM
        next_run = start_date.replace(hour=14, minute=0, second=0, microsecond=0)
        
        return next_run


class SimpleTimetablePlugin(AirflowPlugin):
    name = "simple_timetable"
    timetables = [TuesdayThursdayTimetable]
