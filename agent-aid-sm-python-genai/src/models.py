from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from .database import Base
import datetime

class Epic(Base):
    __tablename__ = "epics"
    epic_id = Column(String, primary_key=True)
    title = Column(String)
    description = Column(Text)
    product_owner = Column(String)
    planned_start_date = Column(DateTime)
    planned_end_date = Column(DateTime)
    actual_start_date = Column(DateTime)
    actual_end_date = Column(DateTime)
    status = Column(String)
    blockers = Column(JSON) # List of strings
    stories = Column(JSON) # List of jiraIds

class Story(Base):
    __tablename__ = "stories"
    jira_id = Column(String, primary_key=True)
    epic_id = Column(String, ForeignKey("epics.epic_id"))
    title = Column(String)
    description = Column(Text)
    acceptance_criteria = Column(JSON)
    story_points = Column(Integer)
    priority = Column(String)
    assignee = Column(String)
    type = Column(String)
    status = Column(String)
    created_at = Column(DateTime)
    updated_at = Column(DateTime)
    comments = Column(JSON)
    commits = Column(JSON)
    cicd_deployments = Column(JSON)
    on_plan = Column(Integer) # Using integer for simplicity 0/1
    delay_days = Column(Integer)
    defects_linked = Column(JSON)

class Commit(Base):
    __tablename__ = "commits"
    sha = Column(String, primary_key=True)
    jira_id = Column(String)
    author = Column(String)
    timestamp = Column(DateTime)
    message = Column(Text)
    lines_changed = Column(Integer)
    files_changed = Column(JSON)

class CICDBuild(Base):
    __tablename__ = "cicd_builds"
    build_id = Column(String, primary_key=True)
    jira_id = Column(String)
    environment = Column(String)
    status = Column(String)
    timestamp = Column(DateTime)
    duration_seconds = Column(Integer)
    failure_reason = Column(Text)

class StatusHistory(Base):
    __tablename__ = "status_histories"
    id = Column(Integer, primary_key=True, autoincrement=True)
    jira_id = Column(String)
    from_status = Column(String)
    to_status = Column(String)
    timestamp = Column(DateTime)
    duration_hours = Column(Float)

class Defect(Base):
    __tablename__ = "defects"
    defect_id = Column(String, primary_key=True)
    jira_id = Column(String)
    title = Column(String)
    severity = Column(String)
    status = Column(String)
    reopen_count = Column(Integer)
    created_at = Column(DateTime)
    resolved_at = Column(DateTime)

class VectorStore(Base):
    __tablename__ = "vector_store"
    id = Column(Integer, primary_key=True, autoincrement=True)
    content = Column(Text)
    extra_metadata = Column(JSON)
    embedding = Column(Vector(768)) # Gemini embedding-004 is 768 dims
    entity_type = Column(String) # epic, story, etc.
    entity_id = Column(String)
