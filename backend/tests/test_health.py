"""
Tests for health check endpoints
"""
import pytest


class TestHealthEndpoints:
    """Test suite for health check endpoints"""
    
    def test_health_endpoint(self, test_client):
        """Test /health endpoint returns healthy status"""
        response = test_client.get("/health")
        
        assert response.status_code == 200
        assert response.json() == {"status": "healthy"}
    
    def test_health_endpoint_alternative(self, test_client):
        """Test /health_endpoint returns OK status"""
        response = test_client.get("/health_endpoint")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Status OK!"}
