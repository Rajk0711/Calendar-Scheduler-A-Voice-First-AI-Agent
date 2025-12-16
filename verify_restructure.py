import os
import sys
from dotenv import load_dotenv

# Add current dir to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

def verify():
    print("--- Verifying Restructured App ---")
    
    # 1. Check Imports from Core
    try:
        from core.agent import agent_executor
        from core.tools import list_events
        print("Core imports successful")
    except ImportError as e:
        print(f"Import failed: {e}")
        return

    # 2. Check Mock Data
    try:
        events = list_events.invoke({"time_min": "2025-01-01T00:00:00Z", "time_max": "2026-01-01T00:00:00Z"})
        print(f"Mock Events Found: {len(events)}")
        for e in events:
            print(f"   - {e.get('summary')}")
            
        if len(events) < 5:
             print("Warning: Mock events count seems low. Check tools.py")
             
    except Exception as e:
        print(f"Mock data check failed: {e}")

if __name__ == "__main__":
    verify()
