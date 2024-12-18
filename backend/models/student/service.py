# backend/models/student/service.py
from sqlalchemy.orm import Session
from datetime import datetime
from typing import List, Dict, Optional
from .schema import TopicProgress, TopicStatus
from ..domain.service import DomainService
from ...exceptions import (
    TopicNotFoundException,
    PrerequisitesNotMetException,
    MaxAttemptsReachedException
)
from ...config import MAX_QUIZ_ATTEMPTS

class StudentService:
    def __init__(self, domain_service: DomainService):
        # We need DomainService to check prerequisites and topic existence
        self.domain_service = domain_service

    def initialize_progress(self, db: Session) -> None:
        """
        Initialize progress records for all topics if they don't exist.
        This runs when the system is first used.
        """
        # Get all topics from domain model
        all_topics = self._get_all_topic_ids()
        
        # Create progress records for topics that don't have one
        for topic_id in all_topics:
            if not self.get_topic_progress(db, topic_id):
                progress = TopicProgress(topic_id=topic_id)
                db.add(progress)
        
        db.commit()

    def get_all_progress(self, db: Session) -> List[Dict]:
        """
        Get progress status for all topics with their prerequisites status
        """
        progresses = db.query(TopicProgress).all()
        ret = []
        for progress in progresses:
            try:
                available = self.is_topic_available(db, progress.topic_id)
            except PrerequisitesNotMetException as e:
                # If prerequisites aren't met, mark as unavailable but don't raise the error
                available = False
            ret.append({
                "topic_id": progress.topic_id,
                "status": progress.status.value,
                "attempts": progress.attempts,
                "last_attempt": progress.last_attempt,
                "available": available
            })
        
        return ret

    def get_topic_progress(self, db: Session, topic_id: str) -> Optional[TopicProgress]:
        """Get progress for a specific topic, ensuring the topic exists"""
        # verify topic exists in ontology
        if not self.domain_service.get_topic(topic_id):
            raise TopicNotFoundException(topic_id)
            
        return db.query(TopicProgress).filter(TopicProgress.topic_id == topic_id).first()

    def verify_can_attempt_quiz(self, db: Session, topic_id: str) -> None:
        """
        Verify that a student can attempt a quiz for a topic,
        raising appropriate exceptions if they cannot
        """
        progress = self.get_topic_progress(db, topic_id)
        
        if progress and progress.attempts >= MAX_QUIZ_ATTEMPTS:
            raise MaxAttemptsReachedException(topic_id, MAX_QUIZ_ATTEMPTS)
            
        # Check prerequisites
        self.is_topic_available(db, topic_id)
        
    def is_topic_available(self, db: Session, topic_id: str) -> bool:
        """
        Check if a topic is available to learn, raising appropriate exceptions
        for better error handling
        """
        # I promise this actually makes sense:

        # First verify topic exists
        if not self.domain_service.get_topic(topic_id):
            raise TopicNotFoundException(topic_id)
        print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
        # Get prerequisites
        prerequisites = self.domain_service._get_prerequisites(self.domain_service.onto[topic_id])
        
        # Check prerequisites completion
        missing_prerequisites = []
        print(prerequisites)
        for prereq_id in prerequisites:
            print("ZZZZZZZZZZZZZ")
            print(prereq_id)
            print("TTTTTTTTTTT")
            prereq_progress = self.get_topic_progress(db, prereq_id)
            if not prereq_progress or prereq_progress.status != TopicStatus.PASSED:
                missing_prerequisites.append(prereq_id)
        
        if missing_prerequisites:
            raise PrerequisitesNotMetException(topic_id, missing_prerequisites)
            
        return True

    def update_topic_progress(self, db: Session, topic_id: str, passed: bool) -> None:
        """
        Update topic progress after a quiz attempt
        """
        progress = self.get_topic_progress(db, topic_id)
        if progress:
            progress.attempts += 1
            progress.last_attempt = datetime.now()
            progress.status = TopicStatus.PASSED if passed else TopicStatus.FAILED
            db.commit()

    def _get_all_topic_ids(self) -> List[str]:
        """Helper method to get all topic IDs from domain model"""
        def extract_ids(topics):
            result = []
            for topic in topics:
                result.append(topic["id"])
                result.extend(extract_ids(topic["children"]))
            return result
            
        return extract_ids(self.domain_service.get_all_topics())
