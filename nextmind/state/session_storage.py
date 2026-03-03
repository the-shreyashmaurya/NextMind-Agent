from typing import Optional, List
from sqlmodel import Field, SQLModel, create_engine, Session, select
from nextmind.config.settings import settings
import json

class SessionRecord(SQLModel, table=True):
    session_id: str = Field(primary_key=True)
    state_json: str = Field(default="{}")
    status: str = Field(default="running")

engine = create_engine(settings.DATABASE_URL)

def init_db():
    SQLModel.metadata.create_all(engine)

def save_session(session_id: str, state: dict, status: str = "running"):
    with Session(engine) as session:
        record = session.get(SessionRecord, session_id)
        if not record:
            record = SessionRecord(session_id=session_id)
        record.state_json = json.dumps(state)
        record.status = status
        session.add(record)
        session.commit()

def get_session(session_id: str) -> Optional[dict]:
    with Session(engine) as session:
        record = session.get(SessionRecord, session_id)
        if record:
            return json.loads(record.state_json)
        return None
