# backend/models/pedagogical/qa_service.py
from typing import Dict, Optional
from openai import OpenAI
from adaptive_shots import initialize_adaptive_shot_db
from ...config import OPENAI_API_KEY, QA_DATABASE_PATH

class QAService:
    def __init__(self):
        self.shot_db = initialize_adaptive_shot_db(QA_DATABASE_PATH)
        self.client = OpenAI(api_key=OPENAI_API_KEY)
    
    async def get_answer(self, topic_id: str, question: str, domain_service) -> Dict:
        """
        Gets answer for a question about a specific topic, using few-shot learning
        to improve response quality.
        """
        # Get topic details to provide context
        topic = domain_service.onto[topic_id]
        topic_description = domain_service._get_comment(topic)
        
        # Create context-enhanced question
        contextualized_question = (
            f"Given this topic description: '{topic_description}'\n"
            f"Please answer this question: {question}"
        )
        
        # Get few-shot examples
        few_shots_prompt, shot_list = self.shot_db.create_few_shots_prompt(
            prompt=contextualized_question,
            domain=topic_id,
            limit=2
        )
        
        # Get response from OpenAI
        response = await self.client.chat.completions.create(
            model='gpt-4',
            messages=[
                {"role": "system", "content": "You are a helpful tutor explaining concepts about energy storage systems."},
                *shot_list.to_messages(),
                {"role": "user", "content": contextualized_question}
            ]
        )
        
        answer = response.choices[0].message.content
        
        return {
            "question": question,
            "answer": answer,
            "shot_list": shot_list
        }
    
    def register_feedback(
        self, 
        topic_id: str, 
        question: str, 
        answer: str, 
        rating: float,
        shot_list: Optional[list] = None
    ) -> None:
        """
        Registers user feedback for a question-answer pair to improve future responses.
        """
        if not 1 <= rating <= 10:
            raise ValueError("Rating must be between 1 and 10")
            
        self.shot_db.register_prompt(
            prompt=question,
            answer=answer,
            rating=rating,
            domain=topic_id,
            used_shots=shot_list if shot_list else None
        )