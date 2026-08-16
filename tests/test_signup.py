"""
Tests for the signup endpoint (POST /activities/{activity_name}/signup).
"""

import pytest


class TestSignupEndpoint:
    """Tests for POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant(self, test_client, reset_activities):
        """Test successfully signing up a new participant."""
        response = test_client.post(
            "/activities/Chess%20Club/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "newstudent@mergington.edu" in result["message"]
        
        # Verify participant was added
        activities = test_client.get("/activities").json()
        assert "newstudent@mergington.edu" in activities["Chess Club"]["participants"]

    def test_signup_nonexistent_activity(self, test_client, reset_activities):
        """Test signup for a non-existent activity returns 404."""
        response = test_client.post(
            "/activities/NonExistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "detail" in result

    def test_signup_already_enrolled(self, test_client, reset_activities):
        """Test signup fails when email is already enrolled."""
        # michael@mergington.edu is already in Chess Club
        response = test_client.post(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "Already signed up" in result["detail"]

    def test_signup_activity_full(self, test_client, reset_activities):
        """Test signup fails when activity is at capacity."""
        # First, get Tennis Club which has max 10 participants and only 1 current
        response = test_client.get("/activities").json()
        tennis_club = response["Tennis Club"]
        
        # Fill up Tennis Club to capacity
        max_participants = tennis_club["max_participants"]
        current_count = len(tennis_club["participants"])
        
        # Sign up new participants until full
        for i in range(max_participants - current_count):
            email = f"student{i}@mergington.edu"
            response = test_client.post(
                f"/activities/Tennis%20Club/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Next signup should fail
        response = test_client.post(
            "/activities/Tennis%20Club/signup?email=laststudent@mergington.edu"
        )
        assert response.status_code == 400
        assert "full" in response.json()["detail"].lower()

    def test_signup_multiple_different_activities(self, test_client, reset_activities):
        """Test signing up for multiple different activities."""
        email = "versatile@mergington.edu"
        
        # Sign up for Chess Club
        response = test_client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Sign up for Programming Class
        response = test_client.post(
            f"/activities/Programming%20Class/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify participant is in both activities
        activities = test_client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        assert email in activities["Programming Class"]["participants"]

    def test_signup_missing_email_parameter(self, test_client, reset_activities):
        """Test signup with missing email parameter."""
        response = test_client.post("/activities/Chess%20Club/signup")
        # FastAPI will raise a validation error
        assert response.status_code == 422

    def test_signup_empty_email(self, test_client, reset_activities):
        """Test signup with empty email string."""
        response = test_client.post(
            "/activities/Chess%20Club/signup?email="
        )
        assert response.status_code == 200  # Currently app accepts empty strings
        # This could be improved with email validation
