import pytest
from fastapi.testclient import TestClient
from src.app import app, activities

client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    """Reset participant lists to their original state before each test."""
    original = {name: list(data["participants"]) for name, data in activities.items()}
    yield
    for name, original_participants in original.items():
        activities[name]["participants"] = original_participants


# --- GET /activities ---

def test_get_activities_returns_all():
    # Arrange
    expected_count = len(activities)

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    assert len(response.json()) == expected_count


def test_get_activities_includes_expected_fields():
    # Arrange - no setup needed

    # Act
    response = client.get("/activities")

    # Assert
    for activity in response.json().values():
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


# --- POST /activities/{activity_name}/signup ---

def test_signup_success():
    # Arrange
    activity_name = "Chess Club"
    new_email = "new@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/signup?email={new_email}")

    # Assert
    assert response.status_code == 200
    assert new_email in activities[activity_name]["participants"]


def test_signup_unknown_activity_returns_404():
    # Arrange
    unknown_activity = "Unknown Club"
    email = "new@mergington.edu"

    # Act
    response = client.post(f"/activities/{unknown_activity}/signup?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


# --- POST /activities/{activity_name}/unregister ---

def test_unregister_success():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/unregister?email={existing_email}")

    # Assert
    assert response.status_code == 200
    assert existing_email not in activities[activity_name]["participants"]


def test_unregister_unknown_activity_returns_404():
    # Arrange
    unknown_activity = "Unknown Club"
    email = "michael@mergington.edu"

    # Act
    response = client.post(f"/activities/{unknown_activity}/unregister?email={email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_not_registered_returns_400():
    # Arrange
    activity_name = "Chess Club"
    unregistered_email = "notregistered@mergington.edu"

    # Act
    response = client.post(f"/activities/{activity_name}/unregister?email={unregistered_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Participant not found"
