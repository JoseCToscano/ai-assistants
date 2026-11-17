import os
import datetime
import json
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path

# If modifying these scopes, delete the token.json file.
SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

class CalendarAgent:
    """
    Agent for interacting with Google Calendar API.
    """
    
    def __init__(self):
        """Initialize the CalendarAgent with Google Calendar API client."""
        self.creds = None
        self.service = None
        self.initialize_credentials()
    
    def initialize_credentials(self):
        """Initialize Google Calendar API credentials."""
        # The file token.json stores the user's access and refresh tokens
        token_path = Path('token.json')
        credentials_path = Path('gcp-oauth.keys.json')
        
        if token_path.exists():
            self.creds = Credentials.from_authorized_user_info(
                json.loads(token_path.read_text()), SCOPES)
        
        # If there are no (valid) credentials available, let the user log in.
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not credentials_path.exists():
                    raise FileNotFoundError(
                        "Google OAuth credentials file not found. "
                        "Please ensure 'gcp-oauth.keys.json' exists in the project root."
                    )
                
                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_path, SCOPES)
                self.creds = flow.run_local_server(port=0)
            
            # Save the credentials for the next run
            token_path.write_text(json.dumps({
                'token': self.creds.token,
                'refresh_token': self.creds.refresh_token,
                'token_uri': self.creds.token_uri,
                'client_id': self.creds.client_id,
                'client_secret': self.creds.client_secret,
                'scopes': self.creds.scopes
            }))
        
        # Build the Google Calendar API service
        self.service = build('calendar', 'v3', credentials=self.creds)
    
    def list_calendars(self):
        """List all available calendars."""
        if not self.service:
            self.initialize_credentials()
        
        calendars_result = self.service.calendarList().list().execute()
        calendars = calendars_result.get('items', [])
        
        if not calendars:
            return {"message": "No calendars found."}
        
        return {"calendars": [
            {
                "id": calendar['id'],
                "summary": calendar['summary'],
                "primary": calendar.get('primary', False)
            } for calendar in calendars
        ]}
    
    def list_upcoming_events(self, calendar_id='primary', max_results=10):
        """List upcoming events from the specified calendar."""
        if not self.service:
            self.initialize_credentials()
        
        # Get the current time in ISO format
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        
        events_result = self.service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return {"message": f"No upcoming events found for calendar {calendar_id}."}
        
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Format the start and end times
            if 'T' in start:  # This is a datetime, not just a date
                start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                start_formatted = start_dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                start_formatted = start
                
            if 'T' in end:  # This is a datetime, not just a date
                end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
                end_formatted = end_dt.strftime('%Y-%m-%d %H:%M:%S')
            else:
                end_formatted = end
            
            formatted_events.append({
                "summary": event.get('summary', 'No title'),
                "start": start_formatted,
                "end": end_formatted,
                "location": event.get('location', 'No location'),
                "description": event.get('description', 'No description'),
                "id": event['id']
            })
        
        return {"events": formatted_events}

# For testing the module directly
if __name__ == "__main__":
    calendar_agent = CalendarAgent()
    print("Available calendars:")
    print(json.dumps(calendar_agent.list_calendars(), indent=2))
    print("\nUpcoming events:")
    print(json.dumps(calendar_agent.list_upcoming_events(), indent=2)) 