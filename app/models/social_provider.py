from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class SocialProvider(Base):
    __tablename__ = "social_providers"

    # 제공자 고유 ID
    provider_id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True
    )

    # 제공자 코드 (google, kakao, apple)
    provider_code: Mapped[str] = mapped_column(
        String(20), nullable=False, unique=True
    )

    # 제공자 이름
    provider_name: Mapped[str] = mapped_column(
        String(50), nullable=False
    )