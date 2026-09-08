from sqlalchemy import create_engine, text
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config import DATABASE_URL

# 데이터베이스 연결 엔진 생성
# create_engine은 SQLAlchemy의 핵심 객체
# 데이터베이스와의 실제 연결을 처리
engine = create_engine(DATABASE_URL)

# 데이터베이스 세션 생성기(sessionmaker) 생성
# SessionLocal은 데이터베이스와 상호작용할 수 있는 세션 객체를 생성 팩토리
# - autocommit=False: 자동커밋X. 작업 완료후 명시적으로 커밋
# - autoflush=False: 세션에서 데이터를 플러시(데이터베이스에 반영)하지 않음
# - bind=engine: 생성된 엔진을 세션에 연결하여 데이터베이스와 통신 가능하게 함
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# SQLAlchemy ORM 모델의 베이스 클래스 생성
# declarative_base()는 모든 데이터베이스 모델 클래스가 상속받아야 할 기본 클래스입니다.
# 이 클래스는 테이블과 Python 클래스 간의 매핑을 정의합니다.
Base = declarative_base()

# 데이터베이스 세션을 관리하는 함수 정의
# get_db 함수는 FastAPI에서 의존성 주입(Dependency Injection)으로 사용됩니다.
def get_db():
    # SessionLocal()을 호출하여 데이터베이스와의 세션을 생성합니다.
    db = SessionLocal()
    try:
        # yield를 사용해 생성된 세션 객체를 반환합니다.
        # FastAPI 라우트에서 사용자가 데이터베이스 작업을 수행할 수 있도록 세션을 제공.
        yield db
    finally:
        # 작업이 끝난 후 세션을 닫아 데이터베이스 리소스를 해제합니다.
        print("Closing database session")
        db.close()


# DB 연결 확인용 함수
# SELECT 1은 데이터를 변경하지 않고 연결 상태만 확인하는 간단한 SQL이다.
def check_database_connection():
    try:
        # with 문이 끝나면 연결이 자동으로 반환된다.
        with engine.connect() as connection:
            result = connection.execute(text("SELECT 1")).scalar_one()
            database_name = connection.execute(text("SELECT DATABASE()")).scalar_one()

        print(f"DB 연결 성공: {database_name}")
        print(f"SELECT 1 결과: {result}")
    except Exception as error:
        print(f"DB 연결 실패: {error}")


# 이 파일을 모듈로 직접 실행할 때만 연결 확인 함수를 호출한다.
# FastAPI에서 app.database를 import할 때는 실행되지 않는다.
if __name__ == "__main__":
    check_database_connection()
