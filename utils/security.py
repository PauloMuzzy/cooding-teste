from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
import secrets
import hashlib

ph = PasswordHasher()


class SecurityUtils:
    def hash_access_code(self, code: str) -> str:
        return ph.hash(code)

    def verify_access_code(self, plain: str, hashed: str) -> bool:
        try:
            ph.verify(hashed, plain)
            return True
        except VerifyMismatchError:
            return False

    def create_secure_token(self) -> str:
        return secrets.token_urlsafe(48)

    def hash_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()
