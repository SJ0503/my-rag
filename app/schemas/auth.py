from pydantic import BaseModel
# Refresh Token 요청 데이터
class RefreshTokenRequest(BaseModel):
    refresh_token: str

# Google 로그인 요청 데이터
class GoogleLoginRequest(BaseModel):
    id_token: str