def test_admin_login(client):
    payload = {
        "username": "admin",
        "password": "Admin@123"
    }

    response = client.post("/api/v1/admins/login", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert "access_token" in data["data"]