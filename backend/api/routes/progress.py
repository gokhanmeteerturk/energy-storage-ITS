# backend/api/routes/progress.py
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.models.student.service import StudentService
from ...database import get_db
from ...dependencies import get_student_service
from typing import List, Dict

router = APIRouter()

@router.get("/progress", response_model=List[Dict])
def get_progress(
    student_service: StudentService = Depends(get_student_service),
    db: Session = Depends(get_db)
):
    """
    Get the student's progress across all topics. This endpoint provides a comprehensive
    view of the learning journey, showing which topics are completed, failed, or not yet
    started. It's particularly useful for progress tracking and visualization on the
    frontend.
    """
    return student_service.get_all_progress(db)
