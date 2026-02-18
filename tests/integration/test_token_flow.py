def test_token_refresh_flow(client):
    # --- Step 1: Register user ---
    register_payload = {
        "email": "refresh_test@example.com",
        "password": "Password123",
        "role": "user",
    }
    res = client.post("/users", json=register_payload)
    assert res.status_code == 200, res.text
    user_data = res.json()

    # --- Step 2: Login to get access + refresh tokens ---
    login_resp = client.post(
        "/auth/login",
        json={"email": "refresh_test@example.com", "password": "Password123"},
    )
    assert login_resp.status_code == 200, login_resp.text
    tokens = login_resp.json()
    print("token:", tokens)
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # --- Step 3: Access /users/me with access token ---
    me_resp = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_resp.status_code == 200
    me_data = me_resp.json()
    assert me_data["email"] == "refresh_test@example.com"

    # --- Step 4: Use /auth/refresh to get new access token ---
    refresh_resp = client.post(
        "/auth/refresh",
        cookies={"refresh_token": refresh_token},  # simulate browser cookie
        # headers={"Authorization": f"Bearer {access_token}"}  # optional if your endpoint reads header
    )
    assert refresh_resp.status_code == 200
    new_tokens = refresh_resp.json()
    print("new token:", new_tokens)
    new_access = new_tokens["access_token"]
    assert new_access != access_token  # should be a fresh token

    # --- Step 5: Use new access token to call /users/me ---
    me_new_resp = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {new_access}"}
    )
    assert me_new_resp.status_code == 200
    assert me_new_resp.json()["email"] == "refresh_test@example.com"

    # Optional debug print
    print("Original access:", access_token)
    print("New access:", new_access)
