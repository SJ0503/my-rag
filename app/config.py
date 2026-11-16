from pathlib import Path

from decouple import Config, RepositoryEnv

ENV_PATH = Path(__file__).resolve().parent.parent / ".env"
config = Config(RepositoryEnv(str(ENV_PATH)))

DATABASE_URL = config("DATABASE_URL")

GOOGLE_APPLE_CLIENT_ID = config("GOOGLE_APPLE_CLIENT_ID")

