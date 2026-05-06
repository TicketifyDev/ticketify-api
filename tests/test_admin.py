def test_admin_login(client):
    payload = {
        "username": "admin",
        "password": "Admin@123"
    }

    response = client.post(
        "/api/v1/admins/login",
        json=payload
    )

    print("\nResponse JSON:", response.json())

    assert response.status_code == 200

    response_data = response.json()

    assert response_data["status_code"] == 200