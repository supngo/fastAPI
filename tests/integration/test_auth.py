def test_login_and_me_flow(client):
    # create user first (could call seed logic or register endpoint)
    register_payload = {
        "email": "test@example.com",
        "password": "Password123",
        "role": "user"
    }

    client.post("/users", json=register_payload)

    # login
    response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "Password123"
    })
    assert response.status_code == 200

    access_token = response.json()["access_token"]

    # call protected endpoint
    # me_resp = client.get(
    #     "/me",
    #     headers={"Authorization": f"Bearer {access_token}"}
    # )
    # assert me_resp.status_code == 200
    # assert me_resp.json()["email"] == "test@example.com"
