from datetime import datetime

from sqlalchemy import BigInteger, DateTime, String, text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class User(Base):
    __tablename__ = "users"

    # 사용자 고유 ID
    user_id: Mapped[int] = mapped_column(
        BigInteger, primary_key=True, autoincrement=True
    )

    # 사용자 닉네임
    nickname: Mapped[str] = mapped_column(String(50), nullable=False)

    # 권한 및 계정 상태
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'user'")
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default=text("'active'")
    )

    # 생성 및 수정 일시
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP")
    )

    # 마지막 로그인 일시
    last_login_at: Mapped[datetime | None] = mapped_column(
        DateTime, nullable=True
    )