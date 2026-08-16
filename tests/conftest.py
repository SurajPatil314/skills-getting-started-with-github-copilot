"""
Pytest configuration and shared fixtures for API tests.

Handles test client setup and activities state isolation.
"""

import copy
import pytest
from fastapi.testclient import TestClient
from src.app import app, activities


@pytest.fixture
def test_client():
    """
    Provides a FastAPI TestClient for making requests to the app.
    """
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """
    Fixture that saves the original activities state before each test
    and restores it after the test completes.
    
    This ensures test isolation - changes made in one test don't affect others.
    """
    # Save original state (deep copy to avoid reference issues)
    original_activities = copy.deepcopy(activities)
    
    yield  # Test runs here
    
    # Restore original state after test
    activities.clear()
    activities.update(original_activities)
