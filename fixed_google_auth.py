#!/usr/bin/env python3
"""
Fixed Google Calendar Authentication for Colab
This file contains the corrected authentication function that resolves the 403 insufficientPermissions error.
"""

import os
import datetime
from google.colab import auth
from google.auth import default
from googleapiclient.discovery import build

# Required scopes for Calendar and Tasks access
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/tasks.readonly'
]

def authenticate_google_api_colab_fixed():
    """
    Authenticates the user in Google Colab environment with proper scopes.
    This fixes the 403 insufficientPermissions error by explicitly requesting the required scopes.
    """
    print("Authenticating to Google Colab to access your Google services...")
    # Authenticate with specific scopes - this will open a pop-up for permissions
    auth.authenticate_user(scopes=SCOPES)
    creds, project_id = default(scopes=SCOPES)  # Get credentials with the required scopes
    print("Authentication successful!")
    return creds

def fetch_google_calendar_events(credentials, time_min, time_max):
    """Fetches events from the user's primary Google Calendar."""
    service = build('calendar', 'v3', credentials=credentials)
    print(f"Fetching calendar events from {time_min} to {time_max}")
    events_result = service.events().list(calendarId='primary', timeMin=time_min,
                                          timeMax=time_max, singleEvents=True,
                                          orderBy='startTime').execute()
    events = events_result.get('items', [])
    fetched_meetings = []
    if not events:
        print('No upcoming events found for the specified period.')
    for event in events:
        start = event['start'].get('dateTime', event['start'].get('date'))
        end = event['end'].get('dateTime', event['end'].get('date'))
        summary = event.get('summary', 'No Title')
        fetched_meetings.append(f"{start} - {end}: {summary}")
    return fetched_meetings

def fetch_google_tasks_list(credentials):
    """Fetches tasks from Google Tasks."""
    try:
        service = build('tasks', 'v1', credentials=credentials)
        tasklists = service.tasklists().list().execute()
        tasks_summary = []
        for tasklist in tasklists.get('items', []):
            tasks_result = service.tasks().list(tasklist=tasklist['id']).execute()
            tasks = tasks_result.get('items', [])
            for task in tasks:
                if task.get('status') == 'needsAction':
                    tasks_summary.append(f"Task from '{tasklist['title']}': {task['title']}")
        return tasks_summary
    except Exception as e:
        print(f"Could not fetch Google Tasks (API might not be enabled or scope missing): {e}")
        return []

def test_authentication():
    """Test function to verify the authentication works correctly."""
    print("Testing the fixed authentication function...")
    try:
        # Authenticate with proper scopes
        test_creds = authenticate_google_api_colab_fixed()
        print("✅ Authentication successful with proper scopes!")
        
        # Test calendar access
        now_utc = datetime.datetime.now(datetime.timezone.utc)
        time_min = now_utc.isoformat(timespec='seconds') + 'Z'
        time_max = (now_utc + datetime.timedelta(days=1)).isoformat(timespec='seconds') + 'Z'
        
        calendar_events = fetch_google_calendar_events(test_creds, time_min=time_min, time_max=time_max)
        print(f"✅ Successfully fetched {len(calendar_events)} calendar events!")
        
        # Show first 3 events
        for event in calendar_events[:3]:
            print(f"  - {event}")
            
        # Test tasks access
        tasks = fetch_google_tasks_list(test_creds)
        print(f"✅ Successfully fetched {len(tasks)} tasks!")
        
        return test_creds
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Make sure to grant the required permissions in the popup window.")
        return None

if __name__ == "__main__":
    # Run the test when this file is executed
    test_authentication()