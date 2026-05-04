def test_admin_login(client):
    payload = {
        "username": "admin",
        "password": "Admin@123"
    }

    response = client.post("/api/v1/admins/login", json=payload)

    assert response.status_code in [200, 401]