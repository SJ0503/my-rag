
import hashlib
import hmac

import jwt
from jwt.exceptions import (
    InvalidTokenError,
    PyJWKClientError,
)

from app.config import APPLE_BUNDLE_ID


APPLE_ISSUER = "https://appleid.apple.com"
APPLE_KEYS_URL = "https://appleid.apple.com/auth/keys"

apple_jwks = jwt.PyJWKClient(
    APPLE_KEYS_URL,
    cache_jwk_set=True,
)


def verify_apple_token(
    identity_token: str,
    raw_nonce: str,
) -> dict:
    """
    Apple Identity Token 검증.
    """
    try:
        signing_key = (
            apple_jwks.get_signing_key_from_jwt(
                identity_token
            )
        )

        payload = jwt.decode(
            identity_token,
            signing_key.key,
            algorithms=["RS256"],
            audience=APPLE_BUNDLE_ID,
            issuer=APPLE_ISSUER,
            options={
                "require": [
                    "iss",
                    "sub",
                    "aud",
                    "exp",
                ]
            },
        )

        # Apple에 전달한 nonce는 SHA-256 해시값
        expected_nonce = hashlib.sha256(
            raw_nonce.encode("utf-8")
        ).hexdigest()

        received_nonce = payload.get("nonce")

        if (
            not isinstance(received_nonce, str)
            or not hmac.compare_digest(
                received_nonce,
                expected_nonce,
            )
        ):
            raise ValueError(
                "Apple Nonce 검증 실패"
            )

        return {
            "provider_user_id": str(payload["sub"]),
        }

    except InvalidTokenError as error:
        raise ValueError(
            "유효하지 않은 Apple 인증 토큰입니다."
        ) from error
