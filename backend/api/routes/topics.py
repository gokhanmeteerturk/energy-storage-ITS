# backend/api/routes/topics.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.exceptions import PrerequisitesNotMetException
from backend.models.domain.service import DomainService
from backend.models.student.service import StudentService
from ...database import get_db
from ...dependencies import get_domain_service, get_student_service
from typing import List, Dict

router = APIRouter()

@router.get("/topics", response_model=List[Dict])
def get_topics(
    domain_service: DomainService = Depends(get_domain_service),
    student_service: StudentService = Depends(get_student_service),
    db: Session = Depends(get_db)
):
    """
    Get hierarchical list of all topics with their learning status and availability.
    This endpoint provides an overview of the entire learning path, showing both available and locked topics.
    """
    topics = domain_service.get_all_topics()
    
    def add_progress_info(topic_list):
        for topic in topic_list:
            # Get progress status (if it exists)
            progress = student_service.get_topic_progress(db, topic["id"])
            topic["status"] = progress.status.value if progress else "not_started"
            
            # Check availability WITHOUT raising exceptions
            try:
                topic["available"] = student_service.is_topic_available(db, topic["id"])
            except PrerequisitesNotMetException as e:
                # If prerequisites aren't met, mark as unavailable but don't raise the error
                topic["available"] = False
                topic["missing_prerequisites"] = e.missing_prerequisites
            
            # Recursively process children
            if topic["children"]:
                add_progress_info(topic["children"])
        return topic_list
    
    return add_progress_info(topics)

@router.get("/topic/{topic_id}")
def get_topic(
    topic_id: str,
    domain_service: DomainService = Depends(get_domain_service),
    student_service: StudentService = Depends(get_student_service),
    db: Session = Depends(get_db)
):
    """
    Get detailed information about a specific topic.
    This endpoint is used for the learning page.
    """
    # Check if topic is available to learn
    # Since I have amazing error handling i can just do it in two steps

    # now watch
    student_service.is_topic_available(db, topic_id)
    return domain_service.get_topic_details(topic_id)

@router.get("/prerequisites/{topic_id}")
def get_prerequisites(
    topic_id: str,
    domain_service: DomainService = Depends(get_domain_service),
    student_service: StudentService = Depends(get_student_service),
    db: Session = Depends(get_db)
):
    """
    Get prerequisites for a topic and their completion status.
    This is used to show why a topic might be locked.
    """
    prerequisites = domain_service._get_prerequisites(domain_service.onto[topic_id])
    
    return {
        "prerequisites": [
            {
                "topic_id": prereq_id,
                "status": student_service.get_topic_progress(db, prereq_id).status.value
            }
            for prereq_id in prerequisites
        ]
    }
