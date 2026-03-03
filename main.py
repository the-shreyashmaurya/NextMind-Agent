from fastapi import FastAPI, Depends, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uuid
from typing import List, Optional, Dict
from nextmind.api.security import get_api_key
from nextmind.config.settings import settings
from nextmind.graph.research_flow import research_workflow
from nextmind.state.research_state import ResearchState
from nextmind.state.session_storage import init_db, save_session, get_session
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
from contextlib import asynccontextmanager

# Global variables for the graph and checkpointer
research_graph = None
checkpointer = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global research_graph, checkpointer
    init_db()
    # Initialize the async checkpointer using context manager
    async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as saver:
        checkpointer = saver
        # Compile the graph with the checkpointer instance
        research_graph = research_workflow.compile(
            checkpointer=checkpointer, 
            interrupt_before=["QueryGeneratorNode"]
        )
        print("DEBUG: Application started and graph compiled.")
        yield
    print("DEBUG: Application shutdown and checkpointer closed.")

app = FastAPI(title="NextMind: AI Research Gap Identifier", lifespan=lifespan)

# Add CORS middleware to allow access from other devices/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Models for API Input/Output
class ResearchStartRequest(BaseModel):
    field: str

class ResearchStartResponse(BaseModel):
    session_id: str

class TopicSelectionRequest(BaseModel):
    session_id: str
    topic: str

class ProgressResponse(BaseModel):
    session_id: str
    stage: str
    progress_percent: int
    logs: List[dict]
    topics: Optional[List[str]] = None

@app.get("/topics/{session_id}", dependencies=[Depends(get_api_key)])
async def get_topics(session_id: str):
    state = get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    return {"topics": state.get("topics", [])}

class ResultResponse(BaseModel):
    gap: dict
    hypothesis: dict
    novelty: dict

@app.get("/")
async def root():
    return {"message": "NextMind API is running"}

@app.post("/start-research", response_model=ResearchStartResponse, dependencies=[Depends(get_api_key)])
async def start_research(request: ResearchStartRequest, background_tasks: BackgroundTasks):
    session_id = str(uuid.uuid4())
    
    # Initialize state
    initial_state: ResearchState = {
        "session_id": session_id,
        "field": request.field,
        "status": "running",
        "progress_logs": [],
        "progress_percent": 0,
        "stage": "initialization",
        "topics": [],
        "errors": [],
        "retry_counts": {},
        "token_usage": {},
        "cost_usage": {},
        "timestamps": {}
    }
    
    save_session(session_id, initial_state)
    
    # Run graph in background (will stop at QueryGeneratorNode due to interrupt)
    background_tasks.add_task(run_graph, session_id, initial_state)
    
    return {"session_id": session_id}

async def run_graph(session_id: str, state: ResearchState):
    config = {"configurable": {"thread_id": session_id}}
    print(f"DEBUG: Starting graph for session {session_id}")
    try:
        # Use astream to get real-time updates from nodes
        async for event in research_graph.astream(state, config):
            for node_name, node_output in event.items():
                print(f"DEBUG: Node {node_name} finished. Updates: {list(node_output.keys()) if node_output else 'None'}")
                
                # IMPORTANT: Fetch the full merged state from the checkpointer
                current_state = await research_graph.aget_state(config)
                if current_state and current_state.values:
                    # Explicitly check for topics and log them
                    topics = current_state.values.get("topics", [])
                    print(f"DEBUG: Session {session_id} - Node {node_name} - Current Topics count: {len(topics)}")
                    # Save the dictionary representation to our DB
                    save_session(session_id, dict(current_state.values))
        
        print(f"DEBUG: Graph reached an interrupt or finished for session {session_id}")
    except Exception as e:
        print(f"ERROR: Graph execution failed for session {session_id}: {str(e)}")
        # Fetch latest state from our DB to append error
        current_db_state = get_session(session_id) or state
        if "errors" not in current_db_state:
            current_db_state["errors"] = []
        current_db_state["errors"].append(f"Graph execution error: {str(e)}")
        save_session(session_id, current_db_state, status="failed")

@app.post("/select-topic", dependencies=[Depends(get_api_key)])
async def select_topic(request: TopicSelectionRequest, background_tasks: BackgroundTasks):
    state = get_session(request.session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update state with selected topic
    state["selected_topic"] = request.topic
    state["status"] = "resuming"
    save_session(request.session_id, state)
    
    # Resume graph execution
    background_tasks.add_task(resume_graph, request.session_id)
    
    return {"status": "Topic selected, research resuming", "session_id": request.session_id}

async def resume_graph(session_id: str):
    config = {"configurable": {"thread_id": session_id}}
    print(f"DEBUG: Resuming graph for session {session_id}")
    try:
        # Resume by passing None to astream with the same thread_id
        async for event in research_graph.astream(None, config):
            for node_name, node_output in event.items():
                print(f"DEBUG: Node {node_name} finished (resumed)")
                
                # Fetch full merged state from checkpointer
                current_state = await research_graph.aget_state(config)
                if current_state.values:
                    save_session(session_id, dict(current_state.values), 
                                 status="completed" if current_state.values.get("status") == "completed" else "running")
                
        print(f"DEBUG: Graph hit another interrupt or finished for session {session_id}")
            
    except Exception as e:
        print(f"ERROR: Graph resume failed for session {session_id}: {str(e)}")
        current_db_state = get_session(session_id)
        if current_db_state:
            if "errors" not in current_db_state:
                current_db_state["errors"] = []
            current_db_state["errors"].append(f"Graph resume error: {str(e)}")
            save_session(session_id, current_db_state, status="failed")

@app.get("/progress/{session_id}", response_model=ProgressResponse, dependencies=[Depends(get_api_key)])
async def get_progress(session_id: str):
    state = get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "stage": state.get("stage", "unknown"),
        "progress_percent": state.get("progress_percent", 0),
        "logs": state.get("progress_logs", []),
        "topics": state.get("topics", [])
    }

@app.get("/result/{session_id}", response_model=ResultResponse, dependencies=[Depends(get_api_key)])
async def get_result(session_id: str):
    state = get_session(session_id)
    if not state:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # For MVP, we allow getting partial results if they exist
    result = state.get("result", {
        "gap": {},
        "hypothesis": {},
        "novelty": {"score": 0.0, "evidence": []}
    })
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
