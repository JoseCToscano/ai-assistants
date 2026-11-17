#!/usr/bin/env python3
"""
Test script for Google Calendar integration.
This script will authenticate with Google Calendar API and list your calendars and upcoming events.
"""

from agents.calendar_agent import CalendarAgent
import json

def main():
    print("Initializing Calendar Agent...")
    calendar_agent = CalendarAgent()
    
    print("\n=== Available Calendars ===")
    calendars = calendar_agent.list_calendars()
    print(json.dumps(calendars, indent=2))
    
    print("\n=== Upcoming Events ===")
    events = calendar_agent.list_upcoming_events(max_results=5)
    print(json.dumps(events, indent=2))

if __name__ == "__main__":
    main() 