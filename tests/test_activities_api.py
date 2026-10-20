import pytest
from fastapi.testclient import TestClient

import src.app as app_module


@pytest.fixture
def client(monkeypatch):
    test_activities = {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["existing@mergington.edu"],
        }
    }
    monkeypatch.setattr(app_module, "activities", test_activities)

    with TestClient(app_module.app) as test_client:
        yield test_client


def test_get_activities_returns_activity_data(client):
    # Arrange
    expected_activity = {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["existing@mergington.edu"],
    }

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"Chess Club": expected_activity}


def test_signup_adds_participant(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for Chess Club"}
    assert email in activities_response.json()["Chess Club"]["participants"]


def test_signup_rejects_duplicate_participant(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.post("/activities/Chess%20Club/signup", params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"
    assert activities_response.json()["Chess Club"]["participants"].count(email) == 1


def test_signup_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "new@mergington.edu"

    # Act
    response = client.post("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_removes_participant(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})
    activities_response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from Chess Club"}
    assert email not in activities_response.json()["Chess Club"]["participants"]


def test_unregister_returns_not_found_for_unregistered_participant(client):
    # Arrange
    email = "absent@mergington.edu"

    # Act
    response = client.delete("/activities/Chess%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_returns_not_found_for_unknown_activity(client):
    # Arrange
    email = "existing@mergington.edu"

    # Act
    response = client.delete("/activities/Unknown%20Club/signup", params={"email": email})

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
