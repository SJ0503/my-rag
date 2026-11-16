from pydantic import BaseModel


# Google 로그인 요청 데이터
class GoogleLoginRequest(BaseModel):
    id_token: str