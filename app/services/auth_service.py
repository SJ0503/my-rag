
from uuid import uuid4
from datetime import datetime

from sqlalchemy.orm import Session

from app.models.user import User
from app.models.social_provider import SocialProvider
from app.models.social_account import SocialAccount


def login_with_google(db: Session, google_user: dict):
    """
    Google 로그인 및 회원가입 처리

    기존 회원:
        - 회원 정보 조회
        - 마지막 로그인 시간 갱신

    신규 회원:
        - Google 프로필 이름으로 회원 생성
        - Google 소셜 계정 연결
    """

    # 1. Google 소셜 로그인 제공자 조회
    provider = (
        db.query(SocialProvider)
        .filter(SocialProvider.provider_code == "google")
        .first()
    )

    if provider is None:
        raise LookupError(
            "Google 제공자가 등록되어 있지 않습니다."
        )

    # Google 계정 고유 식별자
    provider_user_id = google_user["provider_user_id"]

    try:
        # 2. 기존 소셜 계정 조회
        social_account = (
            db.query(SocialAccount)
            .filter(
                SocialAccount.provider_id == provider.provider_id,
                SocialAccount.provider_user_id == provider_user_id
            )
            .first()
        )

        now = datetime.now()

        if social_account:
            # 3. 기존 회원 로그인
            user = db.get(User, social_account.user_id)

            if user is None:
                raise RuntimeError(
                    "연결된 사용자가 존재하지 않습니다."
                )

            if user.status != "active":
                raise PermissionError(
                    "비활성화된 계정입니다."
                )

            # 마지막 로그인 시간 갱신
            user.last_login_at = now
            social_account.last_login_at = now

            is_new_user = False

        else:
            # 4. 신규 회원 생성

            # Google 프로필 이름 추출
            google_name = (
                google_user.get("name") or ""
            ).strip()

            # Google 이름이 있으면 사용
            # 이름이 없으면 임시 닉네임 생성
            nickname = (
                google_name[:50]
                if google_name
                else f"lenary_{uuid4().hex[:12]}"
            )

            # 5. 사용자 객체 생성
            user = User(
                nickname=nickname
            )

            # users 테이블에 사용자 추가
            db.add(user)

            # INSERT 후 생성된 user_id 확보
            db.flush()

            # 6. Google 소셜 계정 연결
            social_account = SocialAccount(
                user_id=user.user_id,
                provider_id=provider.provider_id,
                provider_user_id=provider_user_id,
                last_login_at=now
            )

            db.add(social_account)

            # 마지막 로그인 시간 기록
            user.last_login_at = now

            is_new_user = True

        # 7. 데이터베이스 변경사항 저장
        db.commit()

        # 8. 저장된 회원 정보 갱신
        db.refresh(user)

        # 9. 회원 정보 및 신규 가입 여부 반환
        return user, is_new_user

    except Exception:
        # 오류 발생 시 DB 변경사항 취소
        db.rollback()
        raise
