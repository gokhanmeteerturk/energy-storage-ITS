# backend/dependencies.py
from functools import lru_cache
from .models.domain.service import DomainService
from .models.student.service import StudentService
from .models.pedagogical.service import PedagogicalService
from .models.pedagogical.qa_service import QAService

@lru_cache()
def get_qa_service() -> QAService:
    """Creates a singleton instance of QAService"""
    return QAService()

@lru_cache()
def get_domain_service() -> DomainService:
    """
    Creates a singleton instance of DomainService.
    The lru_cache decorator ensures we only load the ontology once.
    """
    return DomainService()

@lru_cache()
def get_student_service() -> StudentService:
    """Creates a singleton instance of StudentService"""
    return StudentService(get_domain_service())

@lru_cache()
def get_pedagogical_service() -> PedagogicalService:
    """Creates a singleton instance of PedagogicalService"""
    return PedagogicalService(get_domain_service(), get_student_service())