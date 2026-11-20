from pathlib import Path

from decouple import Config, RepositoryEnv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
config = Config(RepositoryEnv(str(ENV_PATH)))

DATABASE_URL = config("DATABASE_URL")

GOOGLE_APPLE_CLIENT_ID = config("GOOGLE_APPLE_CLIENT_ID")

# Google Web OAuth Client ID
GOOGLE_WEB_CLIENT_ID = config("GOOGLE_WEB_CLIENT_ID")

# Apple Bundle ID
APPLE_BUNDLE_ID = config("APPLE_BUNDLE_ID")

# Kakao App ID (숫자형)
KAKAO_APP_ID = config("KAKAO_APP_ID", cast=int)

# Lenary JWT 설정
JWT_SECRET_KEY = config("JWT_SECRET_KEY")
JWT_ALGORITHM = "HS256"

