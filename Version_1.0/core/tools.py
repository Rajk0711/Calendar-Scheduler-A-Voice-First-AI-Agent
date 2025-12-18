import os
import json
import datetime
from typing import Optional, List, Dict
from langchain_core.tools import tool
from google.oauth2 import service_account
from googleapiclient.discovery import build

LOG_DIR = os.path.join(os.path.dirname(__file__), "..", "event_logs")
os.makedirs(LOG_DIR, exist_ok=True)

def cleanup_logs():
    """Delete log files older than 7 days."""
    try:
        now = datetime.datetime.now()
        for filename in os.listdir(LOG_DIR):
            if filename.startswith("event_log_") and filename.endswith(".txt"):
                try:
                    date_str = filename.replace("event_log_", "").replace(".txt", "")
                    file_date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
                    if (now - file_date).days > 7:
                        os.remove(os.path.join(LOG_DIR, filename))
                except ValueError:
                    continue
    except Exception as e:
        print(f"Error during log cleanup: {e}")

def get_calendar_service():
    cleanup_logs() # Trigger cleanup on every service build
    service_account_info = os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not service_account_info:
        return None
    
    try:
        creds_dict = json.loads(service_account_info)
        creds = service_account.Credentials.from_service_account_info(
            creds_dict, scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=creds)
        return service
    except Exception as e:
        print(f"Error creating service: {e}")
        return None

def log_action(action: str, details: str, target_date: Optional[str] = None):
    """Log calendar actions to a daily file in event_logs folder."""
    # Use target_date if provided (YYYY-MM-DD), otherwise fallback to today
    log_date = target_date if target_date else datetime.datetime.now().strftime("%Y-%m-%d")
    log_file = os.path.join(LOG_DIR, f"event_log_{log_date}.txt")
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {action.upper()}: {details}\n"
    
    with open(log_file, "a") as f:
        f.write(log_entry)

@tool
def get_daily_schedule(date_str: str) -> str:
    """
    Get the schedule/logs for a specific date from the event_logs folder.
    Args:
        date_str: Date in YYYY-MM-DD format.
    """
    filename = os.path.join(LOG_DIR, f"event_log_{date_str}.txt")
    if os.path.exists(filename):
        with open(filename, "r") as f:
            return f.read()
    return f"No events recorded for {date_str}."

@tool
def list_events(time_min: str, time_max: str) -> List[Dict]:
    """
    List calendar events for a given date range. Also checks local activity logs for mock events.
    Args:
        time_min: Start time in ISO format (e.g., 2023-10-25T10:00:00Z)
        time_max: End time in ISO format
    """
    all_events = []
    
    # 1. Fetch from Google Calendar if available
    service = get_calendar_service()
    if service:
        try:
            events_result = service.events().list(
                calendarId='primary', timeMin=time_min, timeMax=time_max,
                singleEvents=True, orderBy='startTime'
            ).execute()
            all_events.extend(events_result.get('items', []))
        except Exception as e:
            print(f"Google Calendar API Error: {e}")

    # 2. Extract events from local activity logs for the given range
    try:
        # Normalize ISO strings for fromisoformat (handle Z)
        t_min = time_min.replace("Z", "+00:00")
        t_max = time_max.replace("Z", "+00:00")
        start_date = datetime.datetime.fromisoformat(t_min).date()
        end_date = datetime.datetime.fromisoformat(t_max).date()
        
        current_date = start_date
        while current_date <= end_date:
            date_str = current_date.strftime("%Y-%m-%d")
            log_content = get_daily_schedule.invoke({"date_str": date_str})
            if "No events recorded" not in log_content:
                # Basic parsing of CREATE or MOCK lines to simulate event objects
                for line in log_content.splitlines():
                    if ("CREATE:" in line or "MOCK:" in line) and "Summary:" in line:
                        try:
                            # Parse segments
                            # [timestamp] TYPE: Summary: ..., Start: ..., End: ...
                            # OR [timestamp] MOCK: Summary: ...
                            summary = line.split("Summary: ")[1].split(",")[0].strip()
                            
                            # For MOCK entries from previous migration, they might not have start/end times in the same format
                            # but for regular CREATE/UPDATE they do.
                            start = current_date.isoformat() + "T09:00:00" # Default if not found
                            end = current_date.isoformat() + "T10:00:00"
                            
                            if "Start: " in line:
                                start = line.split("Start: ")[1].split(",")[0].strip()
                            if "End: " in line:
                                end = line.split("End: ")[1].split(",")[0].strip()
                            
                            all_events.append({
                                "summary": summary,
                                "start": {"dateTime": start},
                                "end": {"dateTime": end},
                                "mock": True
                            })
                        except Exception:
                            continue
            current_date += datetime.timedelta(days=1)
    except Exception as e:
        print(f"Error parsing local logs: {e}")

    return all_events

@tool
def create_event(summary: str, start_time: str, end_time: str) -> Dict:
    """
    Schedule a new event on the calendar.
    Args:
        summary: Title of the meeting
        start_time: Start time in ISO format
        end_time: End time in ISO format
    """
    # Extract date for logging (YYYY-MM-DD)
    target_date = start_time.split("T")[0]
    log_action("create", f"Summary: {summary}, Start: {start_time}, End: {end_time}", target_date=target_date)
    
    service = get_calendar_service()
    
    if not service:
        return {"summary": summary, "start": {"dateTime": start_time}, "end": {"dateTime": end_time}, "mock": True}

    event = {
        'summary': summary,
        'start': {'dateTime': start_time},
        'end': {'dateTime': end_time},
    }

    try:
        event = service.events().insert(calendarId='primary', body=event).execute()
        return event
    except Exception as e:
        return {"error": str(e)}

@tool
def update_event(event_id: str, summary: Optional[str] = None, start_time: Optional[str] = None, end_time: Optional[str] = None) -> Dict:
    """
    Update an existing event.
    Args:
        event_id: The ID of the event to update
        summary: New title
        start_time: New start time
        end_time: New end time
    """
    target_date = None
    if start_time:
        target_date = start_time.split("T")[0]
    
    log_action("update", f"ID: {event_id}, Summary: {summary}, Start: {start_time}, End: {end_time}", target_date=target_date)
    
    service = get_calendar_service()
    if not service:
        return {"error": "Update not supported in mock mode"}
    
    try:
        event = service.events().get(calendarId='primary', eventId=event_id).execute()
        
        # If no start_time provided for update, use the existing one for logging accuracy
        if not target_date:
             existing_start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
             if existing_start:
                 target_date = existing_start.split("T")[0]
        
        if summary: event['summary'] = summary
        if start_time: event['start'] = {'dateTime': start_time}
        if end_time: event['end'] = {'dateTime': end_time}
        
        updated_event = service.events().update(calendarId='primary', eventId=event_id, body=event).execute()
        return updated_event
    except Exception as e:
        return {"error": str(e)}

@tool
def delete_event(event_id: str) -> str:
    """
    Delete an event from the calendar.
    Args:
        event_id: The ID of the event to delete
    """
    service = get_calendar_service()
    target_date = None
    
    if service:
        try:
            event = service.events().get(calendarId='primary', eventId=event_id).execute()
            start = event.get('start', {}).get('dateTime') or event.get('start', {}).get('date')
            if start:
                target_date = start.split("T")[0]
        except Exception:
            pass

    log_action("delete", f"ID: {event_id}", target_date=target_date)
    
    if not service:
        return "Delete not supported in mock mode"
    
    try:
        service.events().delete(calendarId='primary', eventId=event_id).execute()
        return f"Event {event_id} deleted successfully."
    except Exception as e:
        return f"Error deleting event: {str(e)}"

@tool
def search_activity_logs(query: str) -> str:
    """
    Scans all daily log files in the 'event_logs' folder for a specific keyword or phrase.
    Use this to find entries like 'Day Off', 'Birthday', 'Townhall', 'Holiday', etc.
    Args:
        query: The keyword or phrase to search for.
    """
    matches = []
    try:
        if not os.path.exists(LOG_DIR):
            return "No activity logs found."
            
        for filename in sorted(os.listdir(LOG_DIR)):
            if filename.startswith("event_log_") and filename.endswith(".txt"):
                file_path = os.path.join(LOG_DIR, filename)
                with open(file_path, "r") as f:
                    lines = f.readlines()
                    for line in lines:
                        if query.lower() in line.lower():
                            # Extract date from filename: event_log_YYYY-MM-DD.txt
                            date_str = filename.replace("event_log_", "").replace(".txt", "")
                            matches.append(f"[{date_str}] {line.strip()}")
        
        if not matches:
            return f"No entries matching '{query}' were found in the logs."
            
        return f"I found the following matches for '{query}':\n" + "\n".join(matches)
    except Exception as e:
        return f"Error searching logs: {e}"

@tool
def check_availability(start_time: str, end_time: str) -> bool:
    """
    Check if a specific time slot is free.
    Args:
        start_time: Start time in ISO format
        end_time: End time in ISO format
    """
    events = list_events.invoke({"time_min": start_time, "time_max": end_time})
    if isinstance(events, list) and len(events) > 0:
        if "error" in events[0]:
            return False
        return False
    return True
