# backend/models/domain/service.py
from owlready2 import get_ontology
from typing import List, Dict, Optional

from backend.exceptions import TopicNotFoundException
from ...config import ONTOLOGY_PATH

class DomainService:
    def __init__(self):
        try:
            self.onto = get_ontology(str(ONTOLOGY_PATH)).load()
            self.root_class = self.onto["EnergyStorageSystem"]
        except Exception as e:
            # While I could create a custom OntologyLoadError, this is more of a system error that should prevent the application from starting, so...
            raise RuntimeError(f"Failed to load ontology: {str(e)}")
    
    def get_all_topics(self) -> List[Dict]:
        """Returns hierarchical list of all topics"""
        return self._build_topic_hierarchy(self.root_class)
        
    # Modify the get_topic_details method in DomainService
    def get_topic_details(self, topic_id: str) -> Dict:
        """Get detailed information about a specific topic"""
        topic = self.onto[topic_id]
        if topic is None:
            raise TopicNotFoundException(topic_id)
            
        return {
            "id": topic.name,
            "description": self._get_comment(topic),
            "properties": self._get_topic_properties(topic),
            "prerequisites": self._get_prerequisites(topic)
        }
    def get_topic(self, topic_id: str):
        """Get a topic from ontology by ID"""
        return self.onto[topic_id]
    
    def _build_topic_hierarchy(self, cls) -> List[Dict]:
        """Recursively builds topic hierarchy"""
        result = []
        for subcls in cls.subclasses():
            topic = {
                "id": subcls.name,
                "description": self._get_comment(subcls),
                "children": self._build_topic_hierarchy(subcls)
            }
            result.append(topic)
        return result
    
    def _get_comment(self, cls) -> str:
        """Get the rdfs:comment annotation, raising an exception if malformed"""
        try:
            comment = cls.comment
            return comment[0] if comment else ""
        except Exception as e:
            # Well since this indicates a problem with the ontology structure...
            raise RuntimeError(f"Error retrieving comment for {cls.name}: {str(e)}")
    
    def _get_topic_properties(self, topic) -> Dict:
        """Get all property values for a topic"""
        properties = {}
        for prop in self.onto.properties():
            if hasattr(topic, prop.name):
                values = getattr(topic, prop.name)
                if values:
                    properties[prop.name] = [value.name for value in values]
        return properties
    
    def _get_prerequisites(self, topic) -> List[str]:
        """Get prerequisites for a topic"""
        prereq_property = self.onto["hasPrerequisite"]
        prerequisites = getattr(topic, prereq_property.name, [])
        return [prereq.name for prereq in prerequisites]
