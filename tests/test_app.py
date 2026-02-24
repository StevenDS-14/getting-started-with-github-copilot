import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for GET /activities endpoint"""
    
    def test_get_activities_returns_all(self, client):
        """Should return all available activities"""
        # Arrange
        expected_activity_count = 9
        
        # Act
        response = client.get("/activities")
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert len(data) == expected_activity_count
        assert "Chess Club" in data
        assert "Programming Class" in data
    
    def test_get_activities_has_correct_structure(self, client):
        """Each activity should have required fields"""
        # Arrange
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        activity = data["Chess Club"]
        
        # Assert
        assert response.status_code == 200
        for field in required_fields:
            assert field in activity
        assert isinstance(activity["participants"], list)
    
    def test_get_activities_includes_participants(self, client):
        """Should include current participant list"""
        # Arrange
        activity_name = "Chess Club"
        expected_participants = ["michael@mergington.edu", "daniel@mergington.edu"]
        
        # Act
        response = client.get("/activities")
        data = response.json()
        chess_club = data[activity_name]
        
        # Assert
        assert response.status_code == 200
        for participant in expected_participants:
            assert participant in chess_club["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Should successfully sign up a new participant"""
        # Arrange
        activity = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={new_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert new_email in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Signup should add participant to activity"""
        # Arrange
        activity = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity}/signup?email={new_email}")
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert new_email in activities_data[activity]["participants"]
    
    def test_signup_duplicate_email_fails(self, client):
        """Should reject duplicate signup for same activity"""
        # Arrange
        activity = "Chess Club"
        duplicate_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={duplicate_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Should fail with 404 for non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        test_email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={test_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"]
    
    def test_signup_same_email_different_activities(self, client):
        """Same email should be able to signup for different activities"""
        # Arrange
        email = "versatile@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/{activity2}/signup?email={email}"
        )
        activities_data = client.get("/activities").json()
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities_data[activity1]["participants"]
        assert email in activities_data[activity2]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self, client):
        """Should successfully remove a participant"""
        # Arrange
        activity = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email_to_remove}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in data["message"]
    
    def test_remove_participant_removes_from_list(self, client):
        """Removal should remove participant from activity"""
        # Arrange
        activity = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity}/participants/{email_to_remove}"
        )
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert email_to_remove not in activities_data[activity]["participants"]
    
    def test_remove_nonexistent_participant_fails(self, client):
        """Should fail when removing non-existent participant"""
        # Arrange
        activity = "Chess Club"
        nonexistent_email = "nothere@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{nonexistent_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in data["detail"]
    
    def test_remove_from_nonexistent_activity_fails(self, client):
        """Should fail with 404 for non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        test_email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{test_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"]
    
    def test_remove_multiple_participants(self, client):
        """Should be able to remove multiple participants"""
        # Arrange
        activity = "Chess Club"
        emails_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
        expected_final_count = 0
        
        # Act
        for email in emails_to_remove:
            client.delete(f"/activities/{activity}/participants/{email}")
        
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert len(activities_data[activity]["participants"]) == expected_final_count


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_signup_then_remove_workflow(self, client):
        """Test complete signup -> remove workflow"""
        # Arrange
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        activities_after_signup = client.get("/activities").json()
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        activities_after_removal = client.get("/activities").json()
        
        # Assert - Signup success and participant added
        assert signup_response.status_code == 200
        assert email in activities_after_signup[activity]["participants"]
        
        # Assert - Removal success and participant removed
        assert remove_response.status_code == 200
        assert email not in activities_after_removal[activity]["participants"]
    
    def test_multiple_signups_and_removals(self, client):
        """Test multiple concurrent operations"""
        # Arrange
        activity = "Programming Class"
        emails = [
            "user1@mergington.edu",
            "user2@mergington.edu",
            "user3@mergington.edu"
        ]
        email_to_remove = emails[1]
        
        # Act - Sign up all users
        for email in emails:
            client.post(f"/activities/{activity}/signup?email={email}")
        
        activities_after_signups = client.get("/activities").json()
        
        # Act - Remove middle user
        client.delete(
            f"/activities/{activity}/participants/{email_to_remove}"
        )
        activities_after_removal = client.get("/activities").json()
        
        # Assert - All users signed up
        for email in emails:
            assert email in activities_after_signups[activity]["participants"]
        
        # Assert - Only middle user removed
        assert emails[0] in activities_after_removal[activity]["participants"]
        assert email_to_remove not in activities_after_removal[activity]["participants"]
        assert emails[2] in activities_after_removal[activity]["participants"]


class TestSignupForActivity:
    """Tests for POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_success(self, client):
        """Should successfully sign up a new participant"""
        # Arrange
        activity = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={new_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Signed up" in data["message"]
        assert new_email in data["message"]
    
    def test_signup_adds_participant(self, client):
        """Signup should add participant to activity"""
        # Arrange
        activity = "Chess Club"
        new_email = "newstudent@mergington.edu"
        
        # Act
        client.post(f"/activities/{activity}/signup?email={new_email}")
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert new_email in activities_data[activity]["participants"]
    
    def test_signup_duplicate_email_fails(self, client):
        """Should reject duplicate signup for same activity"""
        # Arrange
        activity = "Chess Club"
        duplicate_email = "michael@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={duplicate_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client):
        """Should fail with 404 for non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        test_email = "test@mergington.edu"
        
        # Act
        response = client.post(
            f"/activities/{nonexistent_activity}/signup?email={test_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"]
    
    def test_signup_same_email_different_activities(self, client):
        """Same email should be able to signup for different activities"""
        # Arrange
        email = "versatile@mergington.edu"
        activity1 = "Chess Club"
        activity2 = "Programming Class"
        
        # Act
        response1 = client.post(
            f"/activities/{activity1}/signup?email={email}"
        )
        response2 = client.post(
            f"/activities/{activity2}/signup?email={email}"
        )
        activities_data = client.get("/activities").json()
        
        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200
        assert email in activities_data[activity1]["participants"]
        assert email in activities_data[activity2]["participants"]


class TestRemoveParticipant:
    """Tests for DELETE /activities/{activity_name}/participants/{email} endpoint"""
    
    def test_remove_participant_success(self, client):
        """Should successfully remove a participant"""
        # Arrange
        activity = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{email_to_remove}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 200
        assert "Removed" in data["message"]
    
    def test_remove_participant_removes_from_list(self, client):
        """Removal should remove participant from activity"""
        # Arrange
        activity = "Chess Club"
        email_to_remove = "michael@mergington.edu"
        
        # Act
        client.delete(
            f"/activities/{activity}/participants/{email_to_remove}"
        )
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert email_to_remove not in activities_data[activity]["participants"]
    
    def test_remove_nonexistent_participant_fails(self, client):
        """Should fail when removing non-existent participant"""
        # Arrange
        activity = "Chess Club"
        nonexistent_email = "nothere@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{activity}/participants/{nonexistent_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 400
        assert "not signed up" in data["detail"]
    
    def test_remove_from_nonexistent_activity_fails(self, client):
        """Should fail with 404 for non-existent activity"""
        # Arrange
        nonexistent_activity = "Nonexistent Club"
        test_email = "test@mergington.edu"
        
        # Act
        response = client.delete(
            f"/activities/{nonexistent_activity}/participants/{test_email}"
        )
        data = response.json()
        
        # Assert
        assert response.status_code == 404
        assert "not found" in data["detail"]
    
    def test_remove_multiple_participants(self, client):
        """Should be able to remove multiple participants"""
        # Arrange
        activity = "Chess Club"
        emails_to_remove = ["michael@mergington.edu", "daniel@mergington.edu"]
        expected_final_count = 0
        
        # Act
        for email in emails_to_remove:
            client.delete(f"/activities/{activity}/participants/{email}")
        
        response = client.get("/activities")
        activities_data = response.json()
        
        # Assert
        assert len(activities_data[activity]["participants"]) == expected_final_count


class TestIntegration:
    """Integration tests combining multiple operations"""
    
    def test_signup_then_remove_workflow(self, client):
        """Test complete signup -> remove workflow"""
        # Arrange
        email = "workflow@mergington.edu"
        activity = "Chess Club"
        
        # Act - Signup
        signup_response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )
        activities_after_signup = client.get("/activities").json()
        
        # Act - Remove
        remove_response = client.delete(
            f"/activities/{activity}/participants/{email}"
        )
        activities_after_removal = client.get("/activities").json()
        
        # Assert - Signup success and participant added
        assert signup_response.status_code == 200
        assert email in activities_after_signup[activity]["participants"]
        
        # Assert - Removal success and participant removed
        assert remove_response.status_code == 200
        assert email not in activities_after_removal[activity]["participants"]
    
    def test_multiple_signups_and_removals(self, client):
        """Test multiple concurrent operations"""
        # Arrange
        activity = "Programming Class"
        emails = [
            "user1@mergington.edu",
            "user2@mergington.edu",
            "user3@mergington.edu"
        ]
        email_to_remove = emails[1]
        
        # Act - Sign up all users
        for email in emails:
            client.post(f"/activities/{activity}/signup?email={email}")
        
        activities_after_signups = client.get("/activities").json()
        
        # Act - Remove middle user
        client.delete(
            f"/activities/{activity}/participants/{email_to_remove}"
        )
        activities_after_removal = client.get("/activities").json()
        
        # Assert - All users signed up
        for email in emails:
            assert email in activities_after_signups[activity]["participants"]
        
        # Assert - Only middle user removed
        assert emails[0] in activities_after_removal[activity]["participants"]
        assert email_to_remove not in activities_after_removal[activity]["participants"]
        assert emails[2] in activities_after_removal[activity]["participants"]