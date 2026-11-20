
import hashlib
import secrets
from datetime import timedelta
from uuid import uuid4

from fastapi import HTTPException
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.models.refresh_token import RefreshToken, utc_now
from app.models.user import User
from app.services.jwt_service import create_access_token


REFRESH_TOKEN_EXPIRE_DAYS = 60
ACCESS_TOKEN_EXPIRE_SECONDS = 15 * 60


def hash_refresh_token(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def _create_token_pair(
    db: Session,
    user_id: int,
    family_id: str,
) -> dict:
    now = utc_now()

    # 암호학적으로 안전한 Refresh Token 생성
    refresh_token = secrets.token_urlsafe(48)

    db.add(
        RefreshToken(
            user_id=user_id,
            family_id=family_id,
            token_hash=hash_refresh_token(refresh_token),
            expires_at=now + timedelta(
                days=REFRESH_TOKEN_EXPIRE_DAYS
            ),
        )
    )

    access_token = create_access_token(
        user_id=user_id,
        session_id=family_id,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_SECONDS,
    }


def create_session_tokens(
    db: Session,
    user_id: int,
) -> dict:
    # 로그인할 때마다 새로운 세션 생성
    family_id = str(uuid4())

    try:
        tokens = _create_token_pair(
            db, user_id, family_id
        )
        db.commit()
        return tokens
    except Exception:
        db.rollback()
        raise


def _revoke_family(
    db: Session,
    family_id: str,
) -> None:
    # 같은 로그인 세션의 모든 토큰 폐기
    db.execute(
        update(RefreshToken)
        .where(
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
        )
        .values(revoked_at=utc_now())
    )


def rotate_refresh_token(
    db: Session,
    raw_token: str,
) -> dict:
    token_hash = hash_refresh_token(raw_token)
    now = utc_now()

    # 동시 재발급 요청을 직렬화하기 위해 행 잠금
    record = db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .with_for_update()
    )

    if record is None:
        raise HTTPException(
            status_code=401,
            detail="유효하지 않은 Refresh Token입니다.",
        )

    # 이미 사용한 Refresh Token을 재사용한 경우
    if record.revoked_at is not None:
        _revoke_family(db, record.family_id)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="이미 사용된 Refresh Token입니다.",
        )

    # 60일 만료 확인
    if record.expires_at <= now:
        _revoke_family(db, record.family_id)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="Refresh Token이 만료되었습니다.",
        )

    user = db.get(User, record.user_id)

    if user is None or user.status != "active":
        _revoke_family(db, record.family_id)
        db.commit()
        raise HTTPException(
            status_code=401,
            detail="사용할 수 없는 계정입니다.",
        )

    try:
        # 기존 토큰 폐기
        record.revoked_at = now

        # 동일 세션에서 새 토큰 발급
        tokens = _create_token_pair(
            db,
            record.user_id,
            record.family_id,
        )

        db.commit()
        return tokens

    except Exception:
        db.rollback()
        raise


def revoke_refresh_session(
    db: Session,
    raw_token: str,
) -> None:
    token_hash = hash_refresh_token(raw_token)

    record = db.scalar(
        select(RefreshToken)
        .where(RefreshToken.token_hash == token_hash)
        .with_for_update()
    )

    if record is not None:
        _revoke_family(db, record.family_id)

    db.commit()


def is_session_active(
    db: Session,
    user_id: int,
    family_id: str,
) -> bool:
    now = utc_now()

    active_token_id = db.scalar(
        select(RefreshToken.token_id)
        .where(
            RefreshToken.user_id == user_id,
            RefreshToken.family_id == family_id,
            RefreshToken.revoked_at.is_(None),
            RefreshToken.expires_at > now,
        )
        .limit(1)
    )

    return active_token_id is not None
