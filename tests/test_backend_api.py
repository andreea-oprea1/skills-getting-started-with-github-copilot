from src.app import activities


def test_root_redirects_to_static_index(client):
    response = client.get("/", follow_redirects=False)

    assert response.status_code == 307
    assert response.headers["location"] == "/static/index.html"


def test_get_activities_returns_expected_shape(client):
    response = client.get("/activities")
    payload = response.json()

    assert response.status_code == 200
    assert isinstance(payload, dict)
    assert "Chess Club" in payload

    for details in payload.values():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_adds_participant(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    before_count = len(activities[activity_name]["participants"])

    response = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Signed up {email} for {activity_name}"
    assert len(activities[activity_name]["participants"]) == before_count + 1
    assert email in activities[activity_name]["participants"]


def test_signup_unknown_activity_returns_404(client):
    response = client.post("/activities/Unknown%20Activity/signup", params={"email": "a@b.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_signup_duplicate_returns_400(client):
    activity_name = "Programming Class"
    email = "duplicate@mergington.edu"

    first = client.post(f"/activities/{activity_name}/signup", params={"email": email})
    second = client.post(f"/activities/{activity_name}/signup", params={"email": email})

    assert first.status_code == 200
    assert second.status_code == 400
    assert second.json()["detail"] == "Student already signed up for this activity"
    assert activities[activity_name]["participants"].count(email) == 1


def test_delete_unregisters_participant(client):
    activity_name = "Gym Class"
    email = "remove-me@mergington.edu"
    activities[activity_name]["participants"].append(email)

    response = client.delete(f"/activities/{activity_name}/participants", params={"email": email})

    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"
    assert email not in activities[activity_name]["participants"]


def test_delete_unknown_participant_returns_404(client):
    response = client.delete(
        "/activities/Chess%20Club/participants", params={"email": "missing@mergington.edu"}
    )

    assert response.status_code == 404
    assert response.json()["detail"] == "Participant not found in this activity"


def test_delete_unknown_activity_returns_404(client):
    response = client.delete("/activities/Unknown%20Activity/participants", params={"email": "a@b.com"})

    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
