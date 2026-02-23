"""
Tests for the authentication router.

Covers:
  - Successful login / wrong credentials / inactive user
  - Refresh token
  - Password validation (endpoint /validate)
  - User registration
  - Logout
  - Retrieval of authenticated user info
  - Access to protected route without token (401)
"""
import pytest
from httpx import AsyncClient


# ── Login ─────────────────────────────────────────────────────────────────────

class TestLogin:
    async def test_login_success_returns_access_token(self, http_client: AsyncClient, admin_user):
        resp = await http_client.post(
            "/auth/login",
            data={"username": admin_user.email, "password": "AdminPass123"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert "access_token" in body
        assert body["token_type"] == "bearer"

    async def test_login_success_sets_refresh_cookie(self, http_client: AsyncClient, admin_user):
        resp = await http_client.post(
            "/auth/login",
            data={"username": admin_user.email, "password": "AdminPass123"},
        )
        assert "refresh-Token" in resp.cookies

    async def test_login_wrong_password_returns_401(self, http_client: AsyncClient, admin_user):
        resp = await http_client.post(
            "/auth/login",
            data={"username": admin_user.email, "password": "WrongPassword"},
        )
        assert resp.status_code == 401

    async def test_login_nonexistent_user_returns_401(self, http_client: AsyncClient):
        resp = await http_client.post(
            "/auth/login",
            data={"username": "noexiste@test.com", "password": "Password123"},
        )
        assert resp.status_code == 401

    async def test_login_inactive_user_returns_401(self, http_client: AsyncClient, inactive_user):
        resp = await http_client.post(
            "/auth/login",
            data={"username": inactive_user.email, "password": "SomePassword"},
        )
        assert resp.status_code == 401

    async def test_login_invalid_email_format_returns_422(self, http_client: AsyncClient):
        resp = await http_client.post(
            "/auth/login",
            data={"username": "not-an-email", "password": "Password123"},
        )
        assert resp.status_code == 422

    async def test_login_missing_password_returns_422(self, http_client: AsyncClient):
        resp = await http_client.post(
            "/auth/login",
            data={"username": "admin@agrync.test"},
        )
        assert resp.status_code == 422


# ── Refresh token ─────────────────────────────────────────────────────────────

class TestRefreshToken:
    async def test_refresh_returns_new_access_token(self, http_client: AsyncClient, admin_user):
        # Hacer login para obtener la cookie refresh-Token
        login_resp = await http_client.post(
            "/auth/login",
            data={"username": admin_user.email, "password": "AdminPass123"},
        )
        assert login_resp.status_code == 200

        # Usar la cookie existente en el cliente
        resp = await http_client.post("/auth/refresh")
        assert resp.status_code == 201
        assert "access_token" in resp.json()

    async def test_refresh_without_cookie_returns_401(self, http_client: AsyncClient):
        resp = await http_client.post("/auth/refresh")
        assert resp.status_code == 401

    async def test_refresh_with_invalid_token_returns_401(self, http_client: AsyncClient):
        http_client.cookies.set("refresh-Token", "invalid.token.value")
        resp = await http_client.post("/auth/refresh")
        assert resp.status_code == 401


# ── Validate password ─────────────────────────────────────────────────────────

class TestValidatePassword:
    async def test_validate_activates_inactive_user(self, http_client: AsyncClient, inactive_user):
        resp = await http_client.post(
            "/auth/validate",
            json={
                "email": inactive_user.email,
                "password": "NuevaPass123",
                "password_confirmation": "NuevaPass123",
            },
        )
        assert resp.status_code == 201
        assert "Activation successful" in resp.json()["message"]

    async def test_validate_password_mismatch_returns_400(self, http_client: AsyncClient, inactive_user):
        resp = await http_client.post(
            "/auth/validate",
            json={
                "email": inactive_user.email,
                "password": "NuevaPass123",
                "password_confirmation": "OtraPass456",
            },
        )
        assert resp.status_code == 400
        assert "passwords" in resp.json()["detail"].lower()

    async def test_validate_password_too_short_returns_400(self, http_client: AsyncClient, inactive_user):
        resp = await http_client.post(
            "/auth/validate",
            json={
                "email": inactive_user.email,
                "password": "abc",
                "password_confirmation": "abc",
            },
        )
        assert resp.status_code == 400
        assert "8 characters" in resp.json()["detail"]

    async def test_validate_already_active_user_returns_400(self, http_client: AsyncClient, admin_user):
        resp = await http_client.post(
            "/auth/validate",
            json={
                "email": admin_user.email,
                "password": "NuevaPass123",
                "password_confirmation": "NuevaPass123",
            },
        )
        assert resp.status_code == 400
        assert "activated" in resp.json()["detail"].lower()

    async def test_validate_nonexistent_user_returns_403(self, http_client: AsyncClient):
        resp = await http_client.post(
            "/auth/validate",
            json={
                "email": "fantasma@test.com",
                "password": "NuevaPass123",
                "password_confirmation": "NuevaPass123",
            },
        )
        assert resp.status_code == 403


# ── Register ──────────────────────────────────────────────────────────────────

class TestRegister:
    async def test_admin_can_register_new_user(self, http_client: AsyncClient, admin_token):
        resp = await http_client.post(
            "/auth/register",
            json={
                "email": "nuevo@test.com",
                "full_name": "Nuevo Usuario",
                "role": "Lector",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 201
        assert "created" in resp.json()["message"].lower()

    async def test_register_duplicate_email_returns_409(self, http_client: AsyncClient, admin_token, admin_user):
        resp = await http_client.post(
            "/auth/register",
            json={
                "email": admin_user.email,
                "full_name": "Duplicado",
                "role": "Lector",
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 409

    async def test_register_without_auth_returns_401(self, http_client: AsyncClient):
        resp = await http_client.post(
            "/auth/register",
            json={
                "email": "nuevo@test.com",
                "full_name": "Nuevo",
                "role": "Lector",
            },
        )
        assert resp.status_code == 401


# ── Get user info ─────────────────────────────────────────────────────────────

class TestGetUserInfo:
    async def test_authenticated_user_gets_info(self, http_client: AsyncClient, admin_token, admin_user):
        resp = await http_client.get(
            "/auth/info",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["full_name"] == admin_user.full_name
        assert body["role"] == admin_user.role

    async def test_unauthenticated_request_returns_401(self, http_client: AsyncClient):
        resp = await http_client.get("/auth/info")
        assert resp.status_code == 401

    async def test_invalid_token_returns_401(self, http_client: AsyncClient):
        resp = await http_client.get(
            "/auth/info",
            headers={"Authorization": "Bearer invalid.token.here"},
        )
        assert resp.status_code == 401


# ── Logout ────────────────────────────────────────────────────────────────────

class TestLogout:
    async def test_logout_deletes_refresh_cookie(self, http_client: AsyncClient, admin_user):
        await http_client.post(
            "/auth/login",
            data={"username": admin_user.email, "password": "AdminPass123"},
        )
        resp = await http_client.post("/auth/logout")
        assert resp.status_code == 200
        # The cookie should have been deleted (empty value or absent)
        cookie_value = resp.cookies.get("refresh-Token", "")
        assert cookie_value == ""
