#!/usr/bin/env python3
"""
Script to create a recurring gym event at 7 AM every day.
"""

from agents.calendar_agent import CalendarAgent
import datetime
import json
import pytz

def main():
    print("Initializing Calendar Agent...")
    calendar_agent = CalendarAgent()
    
    # Get user's timezone
    # You can change this to your specific timezone if needed
    local_timezone = pytz.timezone('America/Mexico_City')  # Assuming Mexico City timezone based on previous output
    
    # Create start and end times for the event (7 AM to 8 AM)
    # Start with tomorrow to ensure we don't create an event in the past
    tomorrow = datetime.datetime.now(local_timezone) + datetime.timedelta(days=1)
    start_time = tomorrow.replace(hour=7, minute=0, second=0, microsecond=0)
    end_time = tomorrow.replace(hour=8, minute=0, second=0, microsecond=0)
    
    # Create the recurring event
    print("\n=== Creating Recurring Gym Event ===")
    event = calendar_agent.create_recurring_event(
        summary='Gym Workout',
        location='Gym',
        description='Daily morning workout session',
        start_time=start_time,
        end_time=end_time,
        recurrence=['RRULE:FREQ=DAILY'],
        timezone=str(local_timezone)
    )
    
    print("Event created successfully!")
    print(f"Event summary: {event['summary']}")
    print(f"Recurrence: {event['recurrence']}")
    print(f"View in Google Calendar: {event['htmlLink']}")

if __name__ == "__main__":
    main() 