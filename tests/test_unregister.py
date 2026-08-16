"""
Tests for the unregister endpoint (DELETE /activities/{activity_name}/signup).
"""

import pytest


class TestUnregisterEndpoint:
    """Tests for DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_existing_participant(self, test_client, reset_activities):
        """Test successfully unregistering an existing participant."""
        # michael@mergington.edu is already in Chess Club
        response = test_client.delete(
            "/activities/Chess%20Club/signup?email=michael@mergington.edu"
        )
        assert response.status_code == 200
        
        result = response.json()
        assert "message" in result
        assert "michael@mergington.edu" in result["message"]
        
        # Verify participant was removed
        activities = test_client.get("/activities").json()
        assert "michael@mergington.edu" not in activities["Chess Club"]["participants"]

    def test_unregister_nonexistent_activity(self, test_client, reset_activities):
        """Test unregister from a non-existent activity returns 404."""
        response = test_client.delete(
            "/activities/NonExistent%20Club/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        
        result = response.json()
        assert "detail" in result

    def test_unregister_not_enrolled(self, test_client, reset_activities):
        """Test unregister fails when email is not enrolled."""
        response = test_client.delete(
            "/activities/Chess%20Club/signup?email=notonlist@mergington.edu"
        )
        assert response.status_code == 400
        
        result = response.json()
        assert "not signed up" in result["detail"].lower()

    def test_unregister_after_signup(self, test_client, reset_activities):
        """Test signup followed by unregister."""
        email = "tempstudent@mergington.edu"
        
        # Sign up
        response = test_client.post(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify signup
        activities = test_client.get("/activities").json()
        assert email in activities["Chess Club"]["participants"]
        
        # Unregister
        response = test_client.delete(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Verify unregister
        activities = test_client.get("/activities").json()
        assert email not in activities["Chess Club"]["participants"]

    def test_unregister_twice_fails(self, test_client, reset_activities):
        """Test that unregistering twice fails."""
        email = "michael@mergington.edu"
        
        # First unregister succeeds
        response = test_client.delete(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 200
        
        # Second unregister should fail
        response = test_client.delete(
            f"/activities/Chess%20Club/signup?email={email}"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"].lower()

    def test_unregister_frees_capacity(self, test_client, reset_activities):
        """Test that unregistering a participant frees up capacity."""
        activity_name = "Tennis%20Club"
        
        # Get Tennis Club info
        activities = test_client.get("/activities").json()
        tennis = activities["Tennis Club"]
        max_participants = tennis["max_participants"]
        current_count = len(tennis["participants"])
        
        # Fill up Tennis Club
        test_emails = [f"filler{i}@mergington.edu" for i in range(max_participants - current_count)]
        for email in test_emails:
            response = test_client.post(
                f"/activities/{activity_name}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify it's full now
        response = test_client.post(
            f"/activities/{activity_name}/signup?email=overflow@mergington.edu"
        )
        assert response.status_code == 400  # Full
        
        # Unregister one participant
        response = test_client.delete(
            f"/activities/{activity_name}/signup?email={test_emails[0]}"
        )
        assert response.status_code == 200
        
        # Now signup should work again
        response = test_client.post(
            f"/activities/{activity_name}/signup?email=newafter@mergington.edu"
        )
        assert response.status_code == 200

    def test_unregister_missing_email_parameter(self, test_client, reset_activities):
        """Test unregister with missing email parameter."""
        response = test_client.delete("/activities/Chess%20Club/signup")
        # FastAPI will raise a validation error
        assert response.status_code == 422
