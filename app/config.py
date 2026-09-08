from decouple import Config

config = Config(".env")

DATABASE_URL = config("DATABASE_URL")