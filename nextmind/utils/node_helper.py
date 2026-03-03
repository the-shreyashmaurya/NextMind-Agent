from typing import Dict, Any, List
from datetime import datetime
from nextmind.state.research_state import ResearchState

def emit_progress(state: ResearchState, node_name: str, stage: str, percent: int, message: str, meta: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Return state updates for progress.
    """
    progress_event = {
        "timestamp": datetime.utcnow().isoformat(),
        "stage": stage,
        "node": node_name,
        "percent": percent,
        "message": message,
        "meta": meta or {}
    }
    
    return {
        "progress_logs": [progress_event],
        "progress_percent": percent,
        "stage": stage
    }

def update_timestamps(state: ResearchState, node_name: str) -> Dict[str, Any]:
    """
    Return state updates for timestamps.
    """
    return {
        "timestamps": {node_name: datetime.utcnow().isoformat()}
    }
