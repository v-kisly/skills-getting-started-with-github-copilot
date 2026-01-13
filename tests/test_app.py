"""
Tests for the Mergington High School Activities API
"""

import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

# Add src directory to path to import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI app"""
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
    initial_activities = {
        "Soccer": {
            "description": "Team sport focused on soccer skills and competition",
            "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 22,
            "participants": ["alex@mergington.edu"]
        },
        "Basketball": {
            "description": "Basketball training and intramural games",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Art Club": {
            "description": "Explore painting, drawing, and visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater performances and acting workshops",
            "schedule": "Fridays, 4:00 PM - 6:00 PM",
            "max_participants": 20,
            "participants": ["lucas@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and argumentation skills",
            "schedule": "Mondays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 14,
            "participants": ["ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Explore experiments and scientific discoveries",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["noah@mergington.edu"]
        },
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
        }
    }
    
    activities.clear()
    activities.update(initial_activities)
    yield


class TestRootEndpoint:
    """Tests for the root endpoint"""
    
    def test_root_redirect(self, client):
        """Test that root redirects to static/index.html"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307
        assert response.headers["location"] == "/static/index.html"


class TestGetActivities:
    """Tests for the GET /activities endpoint"""
    
    def test_get_all_activities(self, client):
        """Test getting all activities"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        
        # Check that all activities are returned
        assert "Soccer" in data
        assert "Basketball" in data
        assert "Art Club" in data
        assert len(data) == 9
    
    def test_activity_structure(self, client):
        """Test that activities have correct structure"""
        response = client.get("/activities")
        data = response.json()
        
        activity = data["Soccer"]
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity
        assert isinstance(activity["participants"], list)
    
    def test_participants_included(self, client):
        """Test that participants are included in activity data"""
        response = client.get("/activities")
        data = response.json()
        
        soccer = data["Soccer"]
        assert "alex@mergington.edu" in soccer["participants"]


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_successful_signup(self, client):
        """Test successful signup for an activity"""
        response = client.post(
            "/activities/Soccer/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert "student@mergington.edu" in data["message"]
        
        # Verify participant was added
        assert "student@mergington.edu" in activities["Soccer"]["participants"]
    
    def test_signup_nonexistent_activity(self, client):
        """Test signup for nonexistent activity"""
        response = client.post(
            "/activities/NonExistent/signup",
            params={"email": "student@mergington.edu"}
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]
    
    def test_signup_duplicate_participant(self, client):
        """Test signup fails if student already registered"""
        # First signup should succeed
        response1 = client.post(
            "/activities/Soccer/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response1.status_code == 200
        
        # Second signup with same email should fail
        response2 = client.post(
            "/activities/Soccer/signup",
            params={"email": "newstudent@mergington.edu"}
        )
        assert response2.status_code == 400
        assert "already signed up" in response2.json()["detail"]
    
    def test_signup_multiple_activities(self, client):
        """Test student can sign up for multiple activities"""
        email = "versatile@mergington.edu"
        
        # Sign up for Soccer
        response1 = client.post(
            "/activities/Soccer/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for Basketball
        response2 = client.post(
            "/activities/Basketball/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify in both activities
        assert email in activities["Soccer"]["participants"]
        assert email in activities["Basketball"]["participants"]
    
    def test_signup_with_special_characters_in_email(self, client):
        """Test signup with email containing special characters"""
        response = client.post(
            "/activities/Soccer/signup",
            params={"email": "student+test@mergington.edu"}
        )
        assert response.status_code == 200
        assert "student+test@mergington.edu" in activities["Soccer"]["participants"]
    
    def test_initial_participant_count(self, client):
        """Test that initial participant counts are correct"""
        response = client.get("/activities")
        data = response.json()
        
        assert len(data["Soccer"]["participants"]) == 1
        assert len(data["Chess Club"]["participants"]) == 2
        assert len(data["Programming Class"]["participants"]) == 2
