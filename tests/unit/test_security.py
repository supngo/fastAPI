from app.security.security import hash_password, verify_password


def test_hash_password_not_equal():
    token = "mytoken"
    hashed = hash_password(token)
    assert hashed != token


def test_password_verification():
    password = "Secret123"
    hashed = hash_password(password)
    assert verify_password(password, hashed)
