# Core Folder Logic Flowchart

This flowchart details the internal processing logic within the `core` directory, specifically how the agent and tools interact.

```mermaid
flowchart TD
    Start([Input Messages]) --> Agent[chatbot Node]
    
    subgraph LangGraph "langgraph.graph"
        Agent --> Decision{Tool Calls?}
        Decision -- Yes --> ToolExec[tools Node]
        Decision -- No --> End([Final Response])
        ToolExec --> Agent
    end
    
    subgraph ToolSet "tools.py"
        ToolExec --- List[list_events]
        ToolExec --- Create[create_event]
        ToolExec --- Update[update_event]
        ToolExec --- Delete[delete_event]
        ToolExec --- Schedule[get_daily_schedule]
        
        Create --> Logger[log_action]
        Update --> Logger
        Delete --> Logger
        
        Logger --> LogFolder[[event_logs/*.txt]]
        Schedule --> LogRead[Read Log File]
        LogRead --> ToolExec
    end
    
    subgraph Auth_Management "Authentication & Maintenance"
        Service[get_calendar_service] --> Cleanup[cleanup_logs]
        Cleanup --> DeleteOld[Delete files > 7 days]
        Service --> GCreds{Credentials?}
        GCreds -- Service Account --> GAPI[Google API Build]
        GCreds -- User OAuth --> GAPI
        GAPI --> ToolExec
    end
```