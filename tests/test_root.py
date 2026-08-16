"""
Tests for the root endpoint (GET /).
"""

import pytest


class TestRootEndpoint:
    """Tests for GET / endpoint."""

    def test_root_redirect(self, test_client, reset_activities):
        """Test that GET / redirects to /static/index.html."""
        response = test_client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"

    def test_root_redirect_follow(self, test_client, reset_activities):
        """Test that following the redirect returns the HTML page."""
        response = test_client.get("/", follow_redirects=True)
        assert response.status_code == 200
        assert "text/html" in response.headers.get("content-type", "")
