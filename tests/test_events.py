
def test_event_invalid_payload(client):
    payload = {
        "title": ""
    }

    response = client.post("/api/v1/events", json=payload)

    assert response.status_code == 403