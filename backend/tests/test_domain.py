# backend/tests/test_domain.py
import pytest
from ..models.domain.service import DomainService
from ..exceptions import TopicNotFoundException

class TestDomainService:
    @pytest.fixture
    def domain_service(self):
        """Fixture to provide a DomainService instance for tests"""
        return DomainService()
    
    def test_ontology_loading(self, domain_service):
        """Test that ontology is loaded correctly and root class exists"""
        assert domain_service.root_class is not None
        assert domain_service.root_class.name == "EnergyStorageSystem"
    
    def test_get_all_topics(self, domain_service):
        """
        Test that get_all_topics returns a properly structured hierarchy.
        We'll verify both structure and some known content.
        """
        topics = domain_service.get_all_topics()
        
        # Verify we got a list
        assert isinstance(topics, list)
        
        # Verify some known top-level categories exist
        topic_names = [topic["id"] for topic in topics]
        assert "ChemicalEnergyStorage" in topic_names
        assert "MechanicalEnergyStorage" in topic_names
        assert "ThermalEnergyStorage" in topic_names
        
        # Verify each topic has required fields
        for topic in topics:
            assert "id" in topic
            assert "description" in topic
            assert "children" in topic
    
    def test_get_topic_details(self, domain_service):
        """
        Test getting details for a specific topic.
        We'll use a known topic (LithiumIonBatteries) as an example.
        """
        details = domain_service.get_topic_details("LithiumIonBatteries")
        
        # Verify basic structure
        assert details["id"] == "LithiumIonBatteries"
        assert isinstance(details["description"], str)
        assert "properties" in details
        assert "prerequisites" in details
        
        # Verify specific content we know should be there
        assert "BatteryEnergyStorage" in details["prerequisites"]
        assert details["properties"]["hasChargingSpeed"] == ["FastSpeed"]
    
    def test_get_nonexistent_topic(self, domain_service):
        """Test that requesting a non-existent topic raises correct exception"""
        with pytest.raises(TopicNotFoundException):
            domain_service.get_topic_details("NonExistentTopic")
    
    def test_topic_prerequisites(self, domain_service):
        """Test that prerequisites are correctly identified for a topic"""
        prereqs = domain_service._get_prerequisites(
            domain_service.onto["LithiumIonBatteries"]
        )
        assert "BatteryEnergyStorage" in prereqs