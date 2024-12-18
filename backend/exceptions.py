# backend/exceptions.py
from fastapi import HTTPException
from typing import Any, Dict, Optional

class ITSException(Exception):
    """
    Base exception class for our ITS system. All other custom exceptions
    will inherit from this one, making it easier to catch any ITS-specific
    error in a single except block if needed.
    """
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)

class TopicNotFoundException(ITSException):
    """
    Raised when attempting to access a topic that doesn't exist in our ontology.
    This helps distinguish between a topic that truly doesn't exist versus
    other kinds of access errors.
    """
    def __init__(self, topic_id: str):
        super().__init__(f"Topic '{topic_id}' not found in the ontology")

class PrerequisitesNotMetException(ITSException):
    """
    Raised when a student attempts to access a topic without completing
    its prerequisites. This exception includes details about which specific
    prerequisites are missing to provide better feedback to the student.
    """
    def __init__(self, topic_id: str, missing_prerequisites: list[str]):
        self.missing_prerequisites = [''.join([
            ' ' + c if i > 0 and c.isupper() else c 
            for i, c in enumerate(topic)
        ]).strip() for topic in missing_prerequisites]
        prerequisites_str = ", ".join(missing_prerequisites)
        super().__init__(
            f"Cannot access topic '{topic_id}'. "
            f"Must complete the following prerequisites first: {prerequisites_str}"
        )

class MaxAttemptsReachedException(ITSException):
    """
    Raised when a student has reached the maximum number of allowed attempts
    for a quiz. This helps enforce our attempt limits and provide clear
    feedback about why access is denied.
    """
    def __init__(self, topic_id: str, max_attempts: int):
        super().__init__(
            f"Maximum number of attempts ({max_attempts}) reached for topic '{topic_id}'"
        )

class QuizValidationError(ITSException):
    """
    Raised when there are issues with quiz submission format or content.
    This helps catch malformed submissions early and provide clear feedback
    about what's wrong.
    """
    def __init__(self, detail: str):
        super().__init__(f"Quiz validation error: {detail}")

def handle_its_exception(exc: ITSException) -> HTTPException:
    """
    Converts our custom ITS exceptions into FastAPI's HTTPException with
    appropriate status codes. This function serves as a central place to
    map our domain exceptions to HTTP responses.
    """
    exception_map = {
        TopicNotFoundException: 404,
        PrerequisitesNotMetException: 403,
        MaxAttemptsReachedException: 403,
        QuizValidationError: 400
    }
    
    status_code = exception_map.get(type(exc), 500)
    return HTTPException(
        status_code=status_code,
        detail=str(exc)
    )
