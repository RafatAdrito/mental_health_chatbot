"""
Integration tests for JWT auth endpoints.

Requires:
    pip install pytest pytest-asyncio httpx

Run from Backend/ folder:
    pytest tests/test_auth.py -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from app.main import app

SIGNUP_URL = "/api/v1/auth/signup"
LOGIN_URL = "/api/v1/auth/login"
ME_URL = "/api/v1/auth/me"
SESSION_URL = "/api/v1/chat/session"

USER_A = {
    "username": "test_user_a",
    "email": "test_user_a@example.com",
    "password": "SecurePass1!",
}
USER_B = {
    "username": "test_user_b",
    "email": "test_user_b@example.com",
    "password": "AnotherPass2@",
}


@pytest.fixture(scope="module")
def anyio_backend():
    return "asyncio"


@pytest_asyncio.fixture(scope="module")
async def client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="module")
async def token_a(client):
    """Sign up user A and return their access token."""
    resp = await client.post(SIGNUP_URL, json=USER_A)
    assert resp.status_code in (200, 201, 409), resp.text
    if resp.status_code == 409:
        resp = await client.post(LOGIN_URL, json={"email": USER_A["email"], "password": USER_A["password"]})
    return resp.json()["access_token"]


@pytest_asyncio.fixture(scope="module")
async def token_b(client):
    """Sign up user B and return their access token."""
    resp = await client.post(SIGNUP_URL, json=USER_B)
    assert resp.status_code in (200, 201, 409), resp.text
    if resp.status_code == 409:
        resp = await client.post(LOGIN_URL, json={"email": USER_B["email"], "password": USER_B["password"]})
    return resp.json()["access_token"]


# ---------------------------------------------------------------------------
# Signup
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_signup_success(client):
    payload = {
        "username": "signup_unique_xyz",
        "email": "signup_unique_xyz@example.com",
        "password": "ValidPass12!",
    }
    resp = await client.post(SIGNUP_URL, json=payload)
    assert resp.status_code in (200, 201), resp.text
    data = resp.json()
    assert "access_token" in data
    assert data["user"]["email"] == payload["email"]


@pytest.mark.anyio
async def test_signup_duplicate_email(client, token_a):
    payload = {
        "username": "different_user",
        "email": USER_A["email"],  # duplicate
        "password": "SomePass99!",
    }
    resp = await client.post(SIGNUP_URL, json=payload)
    assert resp.status_code == 409


@pytest.mark.anyio
async def test_signup_duplicate_username(client, token_a):
    payload = {
        "username": USER_A["username"],  # duplicate
        "email": "another_unique@example.com",
        "password": "SomePass99!",
    }
    resp = await client.post(SIGNUP_URL, json=payload)
    assert resp.status_code == 409


@pytest.mark.anyio
async def test_signup_weak_password(client):
    payload = {
        "username": "weakpassuser",
        "email": "weakpass@example.com",
        "password": "short",
    }
    resp = await client.post(SIGNUP_URL, json=payload)
    assert resp.status_code == 422  # pydantic validation


@pytest.mark.anyio
async def test_signup_invalid_email(client):
    payload = {
        "username": "bademail_user",
        "email": "not-an-email",
        "password": "ValidPass12!",
    }
    resp = await client.post(SIGNUP_URL, json=payload)
    assert resp.status_code == 422


# ---------------------------------------------------------------------------
# Login
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_login_success(client, token_a):
    resp = await client.post(LOGIN_URL, json={"email": USER_A["email"], "password": USER_A["password"]})
    assert resp.status_code == 200
    data = resp.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.anyio
async def test_login_wrong_password(client):
    resp = await client.post(LOGIN_URL, json={"email": USER_A["email"], "password": "WrongPass!!"})
    assert resp.status_code == 401


@pytest.mark.anyio
async def test_login_unknown_email(client):
    resp = await client.post(LOGIN_URL, json={"email": "ghost@example.com", "password": "SomePass99!"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# /me
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_me_authenticated(client, token_a):
    resp = await client.get(ME_URL, headers={"Authorization": f"Bearer {token_a}"})
    assert resp.status_code == 200
    data = resp.json()
    assert data["email"] == USER_A["email"]


@pytest.mark.anyio
async def test_me_no_token(client):
    resp = await client.get(ME_URL)
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_me_invalid_token(client):
    resp = await client.get(ME_URL, headers={"Authorization": "Bearer invalid.token.here"})
    assert resp.status_code == 401


# ---------------------------------------------------------------------------
# Protected chat routes
# ---------------------------------------------------------------------------

@pytest.mark.anyio
async def test_create_session_requires_auth(client):
    resp = await client.post(SESSION_URL)
    assert resp.status_code == 403


@pytest.mark.anyio
async def test_create_session_authenticated(client, token_a):
    resp = await client.post(SESSION_URL, headers={"Authorization": f"Bearer {token_a}"})
    assert resp.status_code == 200
    assert "session_id" in resp.json()


@pytest.mark.anyio
async def test_cannot_access_other_users_history(client, token_a, token_b):
    # Create a session as user A
    resp = await client.post(SESSION_URL, headers={"Authorization": f"Bearer {token_a}"})
    session_id = resp.json()["session_id"]

    # Try to access it as user B
    resp = await client.get(
        f"/api/v1/chat/history/{session_id}",
        headers={"Authorization": f"Bearer {token_b}"},
    )
    assert resp.status_code in (403, 404)
