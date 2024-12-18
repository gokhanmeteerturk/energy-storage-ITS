# backend/api/routes/qa.py
from fastapi import APIRouter, Depends, HTTPException
from typing import Dict
from pydantic import BaseModel, Field
from ...dependencies import get_qa_service, get_domain_service
from ...exceptions import TopicNotFoundException

router = APIRouter()

class QuestionRequest(BaseModel):
    question: str

class FeedbackRequest(BaseModel):
    question: str
    answer: str
    rating: float = Field(..., ge=1, le=10)
    shot_list: list = None

@router.post("/topic/{topic_id}/ask")
async def ask_question(
    topic_id: str,
    request: QuestionRequest,
    qa_service = Depends(get_qa_service),
    domain_service = Depends(get_domain_service)
):
    """
    Get an AI-generated answer for a question about a specific topic.
    """
    try:
        return await qa_service.get_answer(
            topic_id=topic_id,
            question=request.question,
            domain_service=domain_service
        )

    except KeyError:
        raise TopicNotFoundException(topic_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/topic/{topic_id}/feedback")
def submit_feedback(
    topic_id: str,
    request: FeedbackRequest,
    qa_service = Depends(get_qa_service)
):
    """
    Submit feedback for a question-answer pair to improve future responses.
    """
    try:
        qa_service.register_feedback(
            topic_id=topic_id,
            question=request.question,
            answer=request.answer,
            rating=request.rating,
            shot_list=request.shot_list
        )
        return {"message": "Feedback registered successfully"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))