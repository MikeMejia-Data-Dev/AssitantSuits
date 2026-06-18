from fastapi.testclient import TestClient

from app.main import app
from app.services.auth_service import auth_service


client = TestClient(app)


def setup_function() -> None:
    auth_service._users_by_email.clear()
    auth_service._recovery_tokens.clear()


def test_password_recovery_and_reset_flow() -> None:
    register_response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "user@example.com",
            "password": "StrongPassword123",
            "full_name": "Juan Perez",
            "professional_card": "1234567",
            "role_id": 3,
        },
    )
    assert register_response.status_code == 201

    recovery_response = client.post(
        "/api/v1/auth/password-recovery",
        json={"email": "user@example.com"},
    )
    assert recovery_response.status_code == 200
    assert recovery_response.json()["message"]

    token_record = auth_service.get_recovery_debug("user@example.com")
    assert token_record is not None
    token = token_record.token

    reset_response = client.post(
        "/api/v1/auth/password-reset",
        json={"token": token, "new_password": "EvenStronger456"},
    )
    assert reset_response.status_code == 200

    user = auth_service.authenticate("user@example.com", "EvenStronger456")
    assert user.email == "user@example.com"


def test_password_recovery_is_non_enumerating_for_unknown_email() -> None:
    response = client.post(
        "/api/v1/auth/password-recovery",
        json={"email": "missing@example.com"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "message": "If the email exists, a password recovery token has been generated."
    }


def test_password_reset_rejects_unknown_token() -> None:
    response = client.post(
        "/api/v1/auth/password-reset",
        json={"token": "invalid-token", "new_password": "EvenStronger456"},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid or expired token"
