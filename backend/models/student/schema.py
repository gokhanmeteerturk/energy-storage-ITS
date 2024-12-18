# backend/models/student/schema.py
from sqlalchemy import Boolean, Column, String, Integer, DateTime, Enum
from datetime import datetime
import enum
from ...database import Base

class TopicStatus(enum.Enum):
    NOT_STARTED = "not_started"
    PASSED = "passed"
    FAILED = "failed"

class TopicProgress(Base):
    __tablename__ = "topic_progress"
    
    topic_id = Column(String, primary_key=True)
    status = Column(Enum(TopicStatus), nullable=False, default=TopicStatus.NOT_STARTED)
    attempts = Column(Integer, nullable=False, default=0)
    last_attempt = Column(DateTime, nullable=True)
    
    def __init__(self, topic_id: str):
        self.topic_id = topic_id
        self.status = TopicStatus.NOT_STARTED
        self.attempts = 0

# backend/models/student/schema.py
class QuizSession(Base):
    __tablename__ = "quiz_sessions"
    
    id = Column(String, primary_key=True)
    topic_id = Column(String, nullable=False)
    correct_answers = Column(String, nullable=False)  # JSON string of correct answers
    created_at = Column(DateTime, default=datetime.utcnow)
    completed = Column(Boolean, default=False)
