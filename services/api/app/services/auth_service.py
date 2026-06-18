from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from hashlib import pbkdf2_hmac
import hmac
import secrets
from uuid import uuid4

from app.schemas import RegisterRequest, UserPublic


PASSWORD_RECOVERY_TTL_MINUTES = 30
PBKDF2_ITERATIONS = 100_000


@dataclass
class UserRecord:
    user_id: str
    email: str
    full_name: str
    professional_card: str | None
    role_id: int
    firm_id: str | None
    status: bool
    created_at: datetime
    password_hash: str


@dataclass
class RecoveryTokenRecord:
    email: str
    token: str
    expires_at: datetime


class AuthService:
    def __init__(self) -> None:
        self._users_by_email: dict[str, UserRecord] = {}
        self._recovery_tokens: dict[str, RecoveryTokenRecord] = {}

    def register_user(self, payload: RegisterRequest) -> UserPublic:
        email = payload.email.lower()
        if email in self._users_by_email:
            raise ValueError("Email already registered")

        user = UserRecord(
            user_id=str(uuid4()),
            email=email,
            full_name=payload.full_name,
            professional_card=payload.professional_card,
            role_id=payload.role_id,
            firm_id=None,
            status=True,
            created_at=datetime.now(UTC),
            password_hash=self._hash_password(payload.password),
        )
        self._users_by_email[email] = user
        return self._to_public_user(user)

    def request_password_recovery(self, email: str) -> RecoveryTokenRecord | None:
        normalized_email = email.lower()
        user = self._users_by_email.get(normalized_email)
        if user is None:
            return None

        token = secrets.token_urlsafe(32)
        record = RecoveryTokenRecord(
            email=normalized_email,
            token=token,
            expires_at=datetime.now(UTC) + timedelta(minutes=PASSWORD_RECOVERY_TTL_MINUTES),
        )
        self._recovery_tokens[normalized_email] = record
        return record

    def reset_password(self, token: str, new_password: str) -> None:
        now = datetime.now(UTC)
        record = next(
            (
                item
                for item in self._recovery_tokens.values()
                if item.token == token and item.expires_at >= now
            ),
            None,
        )
        if record is None:
            raise ValueError("Invalid or expired token")

        user = self._users_by_email[record.email]
        user.password_hash = self._hash_password(new_password)
        self._recovery_tokens.pop(record.email, None)

    def authenticate(self, email: str, password: str) -> UserPublic:
        normalized_email = email.lower()
        user = self._users_by_email.get(normalized_email)
        if user is None or not user.status:
            raise ValueError("Invalid credentials")
        if not self._verify_password(password, user.password_hash):
            raise ValueError("Invalid credentials")
        return self._to_public_user(user)

    def get_recovery_debug(self, email: str) -> RecoveryTokenRecord | None:
        return self._recovery_tokens.get(email.lower())

    def _to_public_user(self, user: UserRecord) -> UserPublic:
        return UserPublic(
            user_id=user.user_id,
            email=user.email,
            full_name=user.full_name,
            professional_card=user.professional_card,
            role_id=user.role_id,
            firm_id=user.firm_id,
            status=user.status,
            created_at=user.created_at,
        )

    def _hash_password(self, password: str) -> str:
        salt = secrets.token_bytes(16)
        derived_key = pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            PBKDF2_ITERATIONS,
        )
        return f"{PBKDF2_ITERATIONS}${salt.hex()}${derived_key.hex()}"

    def _verify_password(self, password: str, encoded_hash: str) -> bool:
        iterations_text, salt_hex, stored_hash_hex = encoded_hash.split("$", maxsplit=2)
        derived_key = pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            bytes.fromhex(salt_hex),
            int(iterations_text),
        )
        return hmac.compare_digest(derived_key.hex(), stored_hash_hex)


auth_service = AuthService()
