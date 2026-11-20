
from datetime import datetime, timezone

from sqlalchemy import (
    BigInteger,
    DateTime,
    ForeignKey,
    String,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


def utc_now() -> datetime:
    # MySQL DATETIME에 UTC 기준으로 저장
    return datetime.now(timezone.utc).replace(tzinfo=None)


class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True,
    )

    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("users.user_id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # 하나의 로그인 세션을 구분하는 ID 기기별 로그인 세션 구분
    family_id: Mapped[str] = mapped_column(
        String(36),
        nullable=False,
        index=True,
    )

    # Refresh Token 원문이 아닌 SHA-256 해시
    token_hash: Mapped[str] = mapped_column(
        String(64),
        unique=True,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=utc_now,
    )
    # 만료 시각
    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )
    # 사용 완료·로그아웃 등으로 폐기된 시각
    revoked_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True,
    )
