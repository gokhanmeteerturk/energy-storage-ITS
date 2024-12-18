# backend/api/routes/quiz.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.config import MAX_QUIZ_ATTEMPTS
from backend.models.pedagogical.service import PedagogicalService
from backend.models.student.service import StudentService
from ...database import get_db
from ...dependencies import get_pedagogical_service, get_student_service
from typing import List, Dict
from pydantic import BaseModel

class QuizAnswer(BaseModel):
    selected: str

class QuizSubmission(BaseModel):
    answers: List[QuizAnswer]

router = APIRouter()

@router.get("/quiz/{topic_id}")
def get_quiz(
    topic_id: str,
    pedagogical_service: PedagogicalService = Depends(get_pedagogical_service),
    student_service: StudentService = Depends(get_student_service),
    db: Session = Depends(get_db)
):
    """
    Generate a quiz for a specific topic. This endpoint creates a personalized assessment
    that tests the student's understanding of both the topic's core concepts and its
    specific properties. The quiz includes multiple types of questions to provide
    comprehensive evaluation.
    
    The endpoint also performs important validations:
    - Checks if the topic is available to learn
    - Ensures the student hasn't exceeded maximum attempts
    - Verifies the topic exists in our domain model
    """
    student_service.verify_can_attempt_quiz(db, topic_id)
    return pedagogical_service.generate_quiz(db, topic_id)

@router.post("/quiz/{quiz_id}/submit")
def submit_quiz(
    quiz_id: str,
    submission: QuizSubmission,
    pedagogical_service: PedagogicalService = Depends(get_pedagogical_service),
    db: Session = Depends(get_db)
):
    """Submit quiz answers and get results"""
    answers = [{"selected": answer.selected} for answer in submission.answers]
    return pedagogical_service.evaluate_quiz(db, quiz_id, answers)
