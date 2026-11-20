
from datetime import datetime
from uuid import uuid4

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.social_provider import SocialProvider
from app.models.social_account import SocialAccount


def login_with_social(
    db: Session,
    provider_code: str,
    social_user: dict,
):
    """
    Google, Kakao, Apple 공통 회원 처리.

    소셜 제공자와 제공자별 사용자 ID를 기준으로
    각각 독립된 Lenary 회원 계정을 관리한다.
    """
    provider = (
        db.query(SocialProvider)
        .filter(
            SocialProvider.provider_code == provider_code
        )
        .first()
    )

    if provider is None:
        raise LookupError(
            f"{provider_code} 제공자가 등록되어 있지 않습니다."
        )

    provider_user_id = str(
        social_user["provider_user_id"]
    )

    now = datetime.now()

    try:
        social_account = (
            db.query(SocialAccount)
            .filter(
                SocialAccount.provider_id == provider.provider_id,
                SocialAccount.provider_user_id == provider_user_id,
            )
            .first()
        )

        if social_account:
            user = db.get(
                User,
                social_account.user_id,
            )

            if user is None:
                raise RuntimeError(
                    "연결된 사용자가 존재하지 않습니다."
                )

            if user.status != "active":
                raise PermissionError(
                    "비활성화된 계정입니다."
                )

            user.last_login_at = now
            social_account.last_login_at = now
            is_new_user = False

        else:
            name = (
                social_user.get("name") or ""
            ).strip()

            nickname = (
                name[:50]
                if name
                else f"lenary_{uuid4().hex[:12]}"
            )

            user = User(
                nickname=nickname,
                last_login_at=now,
            )

            db.add(user)
            db.flush()

            social_account = SocialAccount(
                user_id=user.user_id,
                provider_id=provider.provider_id,
                provider_user_id=provider_user_id,
                last_login_at=now,
            )

            db.add(social_account)
            is_new_user = True

        db.commit()
        db.refresh(user)

        return user, is_new_user

    except Exception:
        db.rollback()
        raise


# 기존 Google 로그인 호출부와 호환
def login_with_google(
    db: Session,
    google_user: dict,
):
    return login_with_social(
        db,
        "google",
        google_user,
    )
