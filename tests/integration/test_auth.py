import uuid

def test_login_and_me_flow(client):
    # create user first (could call seed logic or register endpoint)
    register_payload = {
        "email": "test@example.com",
        "password": "Password123",
        "role": "user",
    }

    response = client.post("/users", json=register_payload)
    assert response.status_code == 200, response.text

    user_data = response.json()
    # print("REGISTER RESPONSE:", user_data)

    # login
    login_response = client.post("/auth/login", json={
        "email": "test@example.com",
        "password": "Password123"
    })
    assert login_response.status_code == 200, login_response.text
    tokens = login_response.json()
    print("LOGIN RESPONSE:", tokens)
    access_token = tokens["access_token"]

    # call protected endpoint
    me_resp = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    # print("ME RESPONSE:", me_resp.status_code, me_resp.json())
    assert me_resp.status_code == 200
    me_data = me_resp.json()

    # --- Step 4: Validate returned user matches registration ---
    assert me_data["email"] == "test@example.com"
    assert uuid.UUID(me_data["id"])  # Ensure ID is a valid UUID
