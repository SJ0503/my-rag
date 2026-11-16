from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Integer,
    String,
    DateTime,
    ForeignKey,
    UniqueConstraint,
    text,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SocialAccount(Base):
    __tablename__ = "social_accounts"

    # DB에 정의된 복합 UNIQUE 제약조건
    __table_args__ = (
        UniqueConstraint(
            "provider_id",
            "provider_user_id",
            name="uq_social_provider_user"
        ),
        UniqueConstraint(
            "user_id",
            "provider_id",
            name="uq_user_provider"
        ),
    )

    # 소셜 계정 고유 ID
    social_account_id: Mapped[int] = mapped_column(
        BigInteger,
        primary_key=True,
        autoincrement=True
    )

    # users 테이블과 연결
    user_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey(
            "users.user_id",
            ondelete="CASCADE",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    # social_providers 테이블과 연결
    provider_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey(
            "social_providers.provider_id",
            ondelete="RESTRICT",
            onupdate="CASCADE"
        ),
        nullable=False
    )

    # Google sub 등 소셜 사용자 고유 ID
    provider_user_id: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    # 최초 계정 연결 일시
    linked_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP")
    )

    # 마지막 로그인 일시
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )