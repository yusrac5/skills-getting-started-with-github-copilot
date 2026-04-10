import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

# Initial state of activities for resetting
initial_activities = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    },
    "Basketball Team": {
        "description": "Competitive basketball team for intramural and inter-school games",
        "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
    },
    "Track and Field": {
        "description": "Running, jumping, and throwing events for athletic development",
        "schedule": "Mondays, Wednesdays, Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 25,
        "participants": ["tyler@mergington.edu", "jessica@mergington.edu"]
    },
    "Art Studio": {
        "description": "Explore painting, drawing, and other visual arts",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["isabella@mergington.edu"]
    },
    "Music Band": {
        "description": "Learn and perform music with the school band",
        "schedule": "Mondays and Thursdays, 4:00 PM - 5:00 PM",
        "max_participants": 25,
        "participants": ["noah@mergington.edu", "aria@mergington.edu"]
    },
    "Mathematics Club": {
        "description": "Solve challenging math problems and prepare for competitions",
        "schedule": "Tuesdays, 3:30 PM - 4:30 PM",
        "max_participants": 18,
        "participants": ["liam@mergington.edu"]
    },
    "Science Olympiad": {
        "description": "Compete in science-based academic competitions",
        "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 20,
        "participants": ["mia@mergington.edu", "lucas@mergington.edu"]
    }
}

@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test."""
    activities.clear()
    activities.update(initial_activities)

@pytest.fixture
def client():
    """Test client for the FastAPI app."""
    return TestClient(app)

def test_get_activities(client):
    response = client.get("/activities")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "Chess Club" in data
    assert data["Chess Club"]["description"] == "Learn strategies and compete in chess tournaments"
    assert len(data["Chess Club"]["participants"]) == 2

def test_root_redirect(client):
    response = client.get("/", follow_redirects=False)
    assert response.status_code == 307  # Temporary redirect
    assert response.headers["location"] == "/static/index.html"

def test_signup_success(client):
    response = client.post("/activities/Chess Club/signup?email=new@student.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Signed up new@student.edu for Chess Club" in data["message"]
    # Verify added
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "new@student.edu" in activities_data["Chess Club"]["participants"]

def test_signup_duplicate(client):
    response = client.post("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Student already signed up"

def test_signup_activity_full(client):
    # Fill up an activity (e.g., Basketball Team has 1 spot, max 15, but to test full, need to add more)
    # Basketball has 1 participant, max 15, so add 14 more
    for i in range(14):
        client.post(f"/activities/Basketball Team/signup?email=test{i}@edu")
    # Now it's full
    response = client.post("/activities/Basketball Team/signup?email=overflow@edu")
    assert response.status_code == 400
    data = response.json()
    assert data["detail"] == "Activity is full"

def test_signup_activity_not_found(client):
    response = client.post("/activities/Nonexistent Activity/signup?email=test@edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_unregister_success(client):
    response = client.delete("/activities/Chess Club/signup?email=michael@mergington.edu")
    assert response.status_code == 200
    data = response.json()
    assert "Unregistered michael@mergington.edu from Chess Club" in data["message"]
    # Verify removed
    get_response = client.get("/activities")
    activities_data = get_response.json()
    assert "michael@mergington.edu" not in activities_data["Chess Club"]["participants"]

def test_unregister_activity_not_found(client):
    response = client.delete("/activities/Nonexistent Activity/signup?email=test@edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Activity not found"

def test_unregister_participant_not_found(client):
    response = client.delete("/activities/Chess Club/signup?email=not@participant.edu")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Participant not found"