from fastapi.testclient import TestClient
from src.app import app

client = TestClient(app, follow_redirects=False)


def test_root_redirect():
    """Test that root endpoint redirects to static HTML"""
    response = client.get("/")
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"


def test_get_activities():
    """Test getting all activities"""
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert "Programming Class" in data
    # Check structure of one activity
    chess_club = data["Chess Club"]
    assert "description" in chess_club
    assert "schedule" in chess_club
    assert "max_participants" in chess_club
    assert "participants" in chess_club
    assert isinstance(chess_club["participants"], list)


def test_signup_success():
    """Test successful signup for an activity"""
    response = client.post("/activities/Basketball Team/signup", params={"email": "newstudent@mergington.edu"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Signed up newstudent@mergington.edu for Basketball Team" == data["message"]


def test_signup_activity_not_found():
    """Test signup for non-existent activity"""
    response = client.post("/activities/Nonexistent Activity/signup", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Activity not found"


def test_signup_already_signed_up():
    """Test signup when student is already signed up"""
    # First signup
    client.post("/activities/Art Club/signup", params={"email": "duplicate@mergington.edu"})
    # Second signup attempt
    response = client.post("/activities/Art Club/signup", params={"email": "duplicate@mergington.edu"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Student already signed up for this activity"


def test_unregister_success():
    """Test successful unregistration from an activity"""
    # First sign up
    client.post("/activities/Drama Club/signup", params={"email": "removeme@mergington.edu"})
    # Then unregister
    response = client.delete("/activities/Drama Club/participants", params={"email": "removeme@mergington.edu"})
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "Removed removeme@mergington.edu from Drama Club" == data["message"]


def test_unregister_activity_not_found():
    """Test unregister from non-existent activity"""
    response = client.delete("/activities/Nonexistent Activity/participants", params={"email": "test@mergington.edu"})
    assert response.status_code == 404
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Activity not found"


def test_unregister_not_signed_up():
    """Test unregister when student is not signed up"""
    response = client.delete("/activities/Debate Club/participants", params={"email": "notsigned@mergington.edu"})
    assert response.status_code == 400
    data = response.json()
    assert "detail" in data
    assert data["detail"] == "Student not signed up for this activity"