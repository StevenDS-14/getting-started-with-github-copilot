import pytest
import sys
from pathlib import Path

# Add src to path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client with fresh activities data"""
    from fastapi.testclient import TestClient
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset activities to initial state before each test"""
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
        "Soccer Team": {
            "description": "Competitive soccer practices and matches",
            "schedule": "Mondays, Wednesdays, 4:00 PM - 6:00 PM",
            "max_participants": 22,
            "participants": ["nathan@mergington.edu", "laura@mergington.edu"]
        },
        "Basketball Club": {
            "description": "Skill development and intra-school games",
            "schedule": "Tuesdays and Thursdays, 5:00 PM - 7:00 PM",
            "max_participants": 15,
            "participants": ["ryan@mergington.edu", "zoe@mergington.edu"]
        },
        "Art Club": {
            "description": "Drawing, painting, and portfolio development",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 18,
            "participants": ["isabella@mergington.edu", "liam@mergington.edu"]
        },
        "Drama Club": {
            "description": "Theater production, rehearsals, and performances",
            "schedule": "Fridays, 4:00 PM - 6:30 PM",
            "max_participants": 25,
            "participants": ["mia@mergington.edu", "ethan@mergington.edu"]
        },
        "Math Olympiad": {
            "description": "Advanced problem solving and competition preparation",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["oliver@mergington.edu", "ava@mergington.edu"]
        },
        "Science Club": {
            "description": "Experiments, projects, and STEM exploration",
            "schedule": "Tuesdays, 3:30 PM - 5:00 PM",
            "max_participants": 20,
            "participants": ["noah@mergington.edu", "sophia2@mergington.edu"]
        }
    }
    
    # Clear and reset
    activities.clear()
    activities.update(initial_activities)
    
    yield
    
    # Cleanup after test
    activities.clear()
    activities.update(initial_activities)