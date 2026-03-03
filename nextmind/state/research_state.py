from typing import List, Dict, Any, Optional, Annotated
from typing_extensions import TypedDict
import operator

class ResearchState(TypedDict):
    """
    State object for the NextMind LangGraph workflow.
    Defined according to Section 8 of master-rules.md.
    """
    session_id: str
    field: str
    intent: str
    topics: List[str] # Overwrite topics
    selected_topic: str
    queries: List[str] # Overwrite queries
    sources_indexed: Annotated[List[str], operator.add]
    documents: Annotated[List[Dict[str, Any]], operator.add]
    clean_documents: List[Dict[str, Any]] # Overwrite clean docs after dedup
    chunks: Annotated[List[Dict[str, Any]], operator.add]
    embeddings_ready: bool
    vector_ids: Annotated[List[str], operator.add]
    summaries: Annotated[List[str], operator.add]
    concepts: Dict[str, Any]
    coverage_map: Dict[str, Any]
    gaps: List[Dict[str, Any]] # Overwrite gaps
    gap_scores: Dict[str, float]
    selected_gap: Dict[str, Any]
    hypothesis: Dict[str, Any]
    hypothesis_valid: bool
    novelty_queries: List[str]
    novelty_results: Annotated[List[Dict[str, Any]], operator.add]
    similarity_scores: Dict[str, float]
    novelty_score: float
    result: Dict[str, Any]
    
    # Progress and Meta
    progress_logs: Annotated[List[Dict[str, Any]], operator.add]
    progress_percent: Annotated[int, lambda old, new: max(old, new)]
    stage: Annotated[str, lambda old, new: new]
    status: str
    timestamps: Annotated[Dict[str, str], lambda old, new: {**old, **new}]
    errors: Annotated[List[str], operator.add]
    retry_counts: Dict[str, int]
    token_usage: Dict[str, int]
    cost_usage: Dict[str, float]
