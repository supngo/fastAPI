import pytest

def test_logout_flow(client):
    # --- Step 1: Register user ---
    register_payload = {
        "email": "logout_test@example.com",
        "password": "Password123",
        "role": "user",
    }
    res = client.post("/users", json=register_payload)
    assert res.status_code == 200
    user_data = res.json()

    # --- Step 2: Login ---
    login_resp = client.post(
        "/auth/login",
        json={"email": "logout_test@example.com", "password": "Password123"},
    )
    tokens = login_resp.json()
    access_token = tokens["access_token"]
    refresh_token = tokens["refresh_token"]

    # --- Step 3: Call /auth/logout ---
    logout_resp = client.post(
        "/auth/logout",
        cookies={"refresh_token": refresh_token},
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert logout_resp.status_code == 200

    # --- Step 4: Verify refresh token is revoked ---
    refresh_resp = client.post(
        "/auth/refresh",
        cookies={"refresh_token": refresh_token},
    )
    assert refresh_resp.status_code == 401  # should fail, token revoked

    # --- Step 5: Access /users/me still works with existing access token (until it expires) ---
    me_resp = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {access_token}"}
    )
    assert me_resp.status_code == 200
    assert me_resp.json()["email"] == "logout_test@example.com"

    # --- Optional Step 6: Test logout-all ---
    # login again to get a new refresh token
    login2_resp = client.post(
        "/auth/login",
        json={"email": "logout_test@example.com", "password": "Password123"},
    )
    tokens2 = login2_resp.json()
    access2 = tokens2["access_token"]
    refresh2 = tokens2["refresh_token"]

    # call logout-all
    logout_all_resp = client.post(
        "/auth/logout-all",
        headers={"Authorization": f"Bearer {access2}"},
    )
    assert logout_all_resp.status_code == 200

    # verify refresh token is now revoked
    refresh_all_resp = client.post(
        "/auth/refresh",
        cookies={"refresh_token": refresh2},
    )
    assert refresh_all_resp.status_code == 401
