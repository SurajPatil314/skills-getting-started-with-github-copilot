"""
Tests for the activities list endpoint (GET /activities).
"""

import pytest


class TestActivitiesList:
    """Tests for GET /activities endpoint."""

    def test_get_all_activities(self, test_client, reset_activities):
        """Test that GET /activities returns all activities."""
        response = test_client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        assert isinstance(activities, dict)
        # Should have all 9 hardcoded activities
        assert len(activities) == 9
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_activities_have_required_fields(self, test_client, reset_activities):
        """Test that each activity has the required fields."""
        response = test_client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        for activity_name, activity_data in activities.items():
            assert "description" in activity_data
            assert "schedule" in activity_data
            assert "max_participants" in activity_data
            assert "participants" in activity_data
            assert isinstance(activity_data["participants"], list)

    def test_activities_participants_initialized(self, test_client, reset_activities):
        """Test that activities have initial participant lists."""
        response = test_client.get("/activities")
        assert response.status_code == 200
        
        activities = response.json()
        chess_club = activities.get("Chess Club")
        assert chess_club is not None
        assert len(chess_club["participants"]) >= 0
        # Chess Club should have at least the initial participants
        assert "michael@mergington.edu" in chess_club["participants"]
