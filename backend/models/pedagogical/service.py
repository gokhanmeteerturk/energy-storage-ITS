# backend/models/pedagogical/service.py
import json
from typing import List, Dict
import random
import uuid
from sqlalchemy.orm import Session

from backend.models.student.schema import QuizSession
from ..domain.service import DomainService
from ..student.service import StudentService
from ...config import PASS_THRESHOLD, MAX_QUIZ_ATTEMPTS
from ...exceptions import QuizValidationError, TopicNotFoundException


class PedagogicalService:
    def __init__(self, domain_service: DomainService, student_service: StudentService):
        self.domain_service = domain_service
        self.student_service = student_service

    def generate_quiz(self, db: Session, topic_id: str) -> Dict:
        """Generate a quiz for a specific topic"""
        # Verify topic exists
        topic = self.domain_service.get_topic(topic_id)
        if not topic:
            raise TopicNotFoundException(topic_id)
        questions = []
        correct_answers = []

        try:
            # Add description-based question
            desc_question = self._generate_description_question(topic)
            questions.append({
                "question": desc_question["question"],
                "options": desc_question["options"],
                "question_type": "description"
            })
            correct_answers.append(desc_question["correct"])
            # Add property-based questions
            properties = self.domain_service._get_topic_properties(topic)
            for prop_name, values in properties.items():
                if values:
                    prop_question = self._generate_property_question(topic, prop_name, values[0])
                    if prop_question is None:
                        continue
                    questions.append({
                        "question": prop_question["question"],
                        "options": prop_question["options"],
                        "question_type": "property"
                    })
                    correct_answers.append(prop_question["correct"])
            if not questions:
                raise QuizValidationError(
                    'Unable to generate any valid questions for this topic'
                )
            quiz_id = str(uuid.uuid4())
            quiz_session = QuizSession(
                id=quiz_id,
                topic_id=topic_id,
                correct_answers=json.dumps(correct_answers)
            )
            db.add(quiz_session)
            db.commit()
        except Exception as e:
            raise QuizValidationError(f"Error generating quiz: {str(e)}")

        return {
            "quiz_id": quiz_id,
            "topic_id": topic_id,
            "questions": questions
        }


    def evaluate_quiz(self, db: Session, quiz_id: str, answers: List[Dict]) -> Dict:
        """Evaluate quiz answers"""
        quiz_session = db.query(QuizSession).filter_by(id=quiz_id).first()
        if not quiz_session or quiz_session.completed:
            raise QuizValidationError("Invalid or expired quiz session")

        try:
            correct_answers = json.loads(quiz_session.correct_answers)
            
            if len(answers) != len(correct_answers):
                raise QuizValidationError("Number of answers does not match questions")

            correct_count = sum(
                1 for student_answer, correct_answer in zip(answers, correct_answers)
                if student_answer["selected"] == correct_answer
            )
            
            total_questions = len(correct_answers)
            score = correct_count / total_questions
            passed = score >= PASS_THRESHOLD

            # Mark quiz as completed
            quiz_session.completed = True
            
            # Update student progress
            self.student_service.update_topic_progress(db, quiz_session.topic_id, passed)
            
            db.commit()

            return {
                "score": score,
                "passed": passed,
                "correct_count": correct_count,
                "total_questions": total_questions
            }

        except (KeyError, TypeError) as e:
            raise QuizValidationError(f"Invalid answer format: {str(e)}")

    def _generate_description_question(self, topic) -> Dict:
        """
        Generate a question based on topic description
        """
        # Get topic description and sibling descriptions for wrong answers
        correct_desc = self.domain_service._get_comment(topic)
        parent = list(topic.is_a)[0]  # Get direct parent
        sibling_descs = [
            self.domain_service._get_comment(sibling)
            for sibling in parent.subclasses()
            if sibling != topic
        ]

        # Ensure we have enough wrong answers
        while len(sibling_descs) < 3:
            sibling_descs.append(f"None of these are the correct definition")
        # Create question
        options = [correct_desc] + sibling_descs[:3]
        random.shuffle(options)

        return {
            'question': f"Which description best matches {topic.name}?",
            'options': options,
            'correct': correct_desc,
            'type': 'multiple_choice'
        }

    def _generate_property_question(
        self, topic, property_name: str, value: str
    ) -> Dict:
        """
        Generate a question based on topic property
        """
        property_obj = self.domain_service.onto[property_name]
        range_class = property_obj.range[0]
        
        options = [instance.name for instance in range_class.instances()]

        # Format the property name for display
        display_name = ''.join([
            ' ' + c if i > 0 and c.isupper() else c 
            for i, c in enumerate((
            property_name
            .replace("has", "")
            .replace("_", " ")
            .replace("speed", " Speed")
            .replace("suitability", " Suitability")
            .replace("duration", " Duration")
            .strip()
        ))
        ]).strip()
        # Format topic name - add space before capital letters except first one
        formatted_topic_name = ''.join([
            ' ' + c if i > 0 and c.isupper() else c 
            for i, c in enumerate(topic.name)
        ]).strip()
        if display_name == "Prerequisite":
            return None
        return {
            "question": f"What is the {display_name} of {formatted_topic_name}?",
            "options": options,
            "correct": value,
            "type": "property_choice"
        }
