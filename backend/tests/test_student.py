# backend/tests/test_student.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.config import MAX_QUIZ_ATTEMPTS
from backend.models.domain.service import DomainService
from ..models.student.service import StudentService
from ..models.student.schema import Base, TopicProgress, TopicStatus
from ..exceptions import PrerequisitesNotMetException, MaxAttemptsReachedException

class TestStudentService:
    @pytest.fixture
    def db_session(self):
        """Create a test database session"""
        engine = create_engine("sqlite:///:memory:")
        Base.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        session = Session()
        yield session
        session.close()
        
    @pytest.fixture
    def domain_service(self):
        """Fixture for DomainService"""
        return DomainService()
    
    @pytest.fixture
    def student_service(self, domain_service):
        return StudentService(domain_service)
    
    def test_initialize_progress(self, student_service, db_session):
        """Test that progress records are properly initialized"""
        student_service.initialize_progress(db_session)
        
        # Verify every topic has a progress record
        all_topics = student_service._get_all_topic_ids()
        progress_records = db_session.query(TopicProgress).all()
        
        assert len(progress_records) == len(all_topics)
        
        # Verify initial status
        for record in progress_records:
            assert record.status == TopicStatus.NOT_STARTED
            assert record.attempts == 0
    
    def test_topic_availability(self, student_service, db_session):
        """Test prerequisite checking logic"""
        # First initialize progress
        student_service.initialize_progress(db_session)
        
        # Try to access LithiumIonBatteries before completing prerequisite
        with pytest.raises(PrerequisitesNotMetException):
            student_service.is_topic_available(db_session, "LithiumIonBatteries")
        
        # Complete prerequisite
        prereq = db_session.query(TopicProgress).filter_by(
            topic_id="BatteryEnergyStorage"
        ).first()
        prereq.status = TopicStatus.PASSED
        db_session.commit()
        
        # Now topic should be available
        assert student_service.is_topic_available(db_session, "LithiumIonBatteries")
    
    def test_max_attempts(self, student_service, db_session):
        """Test enforcement of maximum quiz attempts"""
        student_service.initialize_progress(db_session)
        
        # Set up a topic with max attempts
        topic = db_session.query(TopicProgress).first()
        topic.attempts = MAX_QUIZ_ATTEMPTS
        db_session.commit()
        
        # Verify we can't attempt another quiz
        with pytest.raises(MaxAttemptsReachedException):
            student_service.verify_can_attempt_quiz(db_session, topic.topic_id)