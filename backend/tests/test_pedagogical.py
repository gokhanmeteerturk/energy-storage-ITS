# backend/tests/test_pedagogical.py
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from backend.models.domain.service import DomainService
from backend.models.student.service import StudentService
from ..models.pedagogical.service import PedagogicalService
from ..models.student.schema import Base, TopicProgress, TopicStatus
from ..exceptions import QuizValidationError, TopicNotFoundException
from ..config import PASS_THRESHOLD

class TestPedagogicalService:
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
        ds = DomainService()
        print("dsdsds")
        print(ds)
        print(type(ds.onto))
        return ds

    @pytest.fixture
    def student_service(self, domain_service):
        """Fixture for StudentService"""
        return StudentService(domain_service)
    
    @pytest.fixture
    def pedagogical_service(self, domain_service, student_service):
        return PedagogicalService(domain_service, student_service)

    def test_quiz_generation(self, db_session, pedagogical_service):
        """
        Test that quizzes are generated with appropriate questions.
        We'll use MechanicalEnergyStorage as an example since it has
        both description and properties.
        """
        quiz = pedagogical_service.generate_quiz(db_session,"MechanicalEnergyStorage")
        
        # Verify basic quiz structure
        assert "quiz_id" in quiz
        assert "questions" in quiz
        assert len(quiz["questions"]) > 0
        
        # Check that we have at least one description question
        desc_questions = [q for q in quiz["questions"] 
                         if "best matches" in q["question"]]
        assert len(desc_questions) == 1
        
        # Verify question structure
        for question in quiz["questions"]:
            assert "question" in question
            assert "options" in question
            assert "question_type" in question
            assert len(question["options"]) > 1

    def test_description_question_generation(self, pedagogical_service):
        """Test specifically the generation of description-based questions"""
        topic = pedagogical_service.domain_service.onto["MechanicalEnergyStorage"]
        question = pedagogical_service._generate_description_question(topic)
        
        # Verify question format
        assert isinstance(question, dict)
        assert "question" in question
        assert "options" in question
        assert len(question["options"]) == 4  # Should have 4 options
        
        # Verify correct answer is among options
        correct_desc = pedagogical_service.domain_service._get_comment(topic)
        assert correct_desc in question["options"]

    def test_property_question_generation(self, pedagogical_service):
        """Test generation of property-based questions"""
        topic = pedagogical_service.domain_service.onto["LithiumIonBatteries"]
        question = pedagogical_service._generate_property_question(
            topic, "hasChargingSpeed", "FastSpeed"
        )
        
        # Verify question structure
        assert "What is the Charging Speed of" in question["question"]
        assert set(question["options"]) == {"FastSpeed", "MediumSpeed", "SlowSpeed"}
        assert question["type"] == "property_choice"
        assert question["correct"] == "FastSpeed"

    def test_nonexistent_topic_quiz(self, db_session, pedagogical_service):
        """Test attempting to generate quiz for nonexistent topic"""
        with pytest.raises(TopicNotFoundException):
            pedagogical_service.generate_quiz(db_session, "NonexistentTopic")