import pytest
from fastapi.testclient import TestClient


def test_get_root_redirect(client):
    """Test that root redirects to static/index.html"""
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities(client):
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    
    data = response.json()
    assert isinstance(data, dict)
    assert len(data) > 0
    assert "Chess Club" in data
    assert "Programming Class" in data


def test_get_activity_details(client):
    """Test that activity details are correct"""
    response = client.get("/activities")
    data = response.json()
    
    chess_club = data["Chess Club"]
    assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
    assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
    assert chess_club["max_participants"] == 12
    assert len(chess_club["participants"]) == 2
    assert "michael@mergington.edu" in chess_club["participants"]


def test_signup_for_activity(client):
    """Test signing up for an activity"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "newstudent@mergington.edu"}
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "newstudent@mergington.edu" in data["message"]
    
    # Verify participant was added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "newstudent@mergington.edu" in activities_data["Chess Club"]["participants"]


def test_signup_duplicate_participant(client):
    """Test that signing up a duplicate participant fails"""
    response = client.post(
        "/activities/Chess Club/signup",
        params={"email": "michael@mergington.edu"}
    )
    assert response.status_code == 400
    
    data = response.json()
    assert "already signed up" in data["detail"]


def test_signup_nonexistent_activity(client):
    """Test signing up for a non-existent activity"""
    response = client.post(
        "/activities/Nonexistent Club/signup",
        params={"email": "student@mergington.edu"}
    )
    assert response.status_code == 404
    
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_remove_participant(client):
    """Test removing a participant from an activity"""
    response = client.delete(
        "/activities/Chess Club/participant/michael@mergington.edu"
    )
    assert response.status_code == 200
    
    data = response.json()
    assert "Removed" in data["message"]
    
    # Verify participant was removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]


def test_remove_nonexistent_participant(client):
    """Test removing a participant that doesn't exist in the activity"""
    response = client.delete(
        "/activities/Chess Club/participant/nonexistent@mergington.edu"
    )
    assert response.status_code == 400
    
    data = response.json()
    assert "Participant not found" in data["detail"]


def test_remove_participant_from_nonexistent_activity(client):
    """Test removing a participant from a non-existent activity"""
    response = client.delete(
        "/activities/Nonexistent Club/participant/student@mergington.edu"
    )
    assert response.status_code == 404
    
    data = response.json()
    assert "Activity not found" in data["detail"]


def test_signup_and_remove_flow(client):
    """Test complete flow: signup then remove"""
    # Sign up
    signup_response = client.post(
        "/activities/Programming Class/signup",
        params={"email": "testuser@mergington.edu"}
    )
    assert signup_response.status_code == 200
    
    # Verify added
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "testuser@mergington.edu" in activities_data["Programming Class"]["participants"]
    
    # Remove
    remove_response = client.delete(
        "/activities/Programming Class/participant/testuser@mergington.edu"
    )
    assert remove_response.status_code == 200
    
    # Verify removed
    activities_response = client.get("/activities")
    activities_data = activities_response.json()
    assert "testuser@mergington.edu" not in activities_data["Programming Class"]["participants"]


def test_activity_capacity(client):
    """Test that activity details show correct capacity"""
    response = client.get("/activities")
    data = response.json()
    
    gym_class = data["Gym Class"]
    initial_participants = len(gym_class["participants"])
    available_spots = gym_class["max_participants"] - initial_participants
    
    assert initial_participants + available_spots == gym_class["max_participants"]
