from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from pydantic import BaseSettings
from urllib.parse import quote_plus, urlparse
import psycopg

class Settings(BaseSettings):
    """애플리케이션 설정"""
    DATABASE_PASSWORD: str = ""
    DATABASE_URL: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()

# DATABASE_URL 구성
if not settings.DATABASE_URL:
    if not settings.DATABASE_PASSWORD:
        raise ValueError(
            "DATABASE_PASSWORD 환경 변수가 설정되지 않았습니다. .env 파일에 DATABASE_PASSWORD를 설정해주세요.\n"
            "또는 Supabase 대시보드에서 제공하는 전체 DATABASE_URL을 .env 파일에 직접 설정할 수 있습니다."
        )
    encoded_password = quote_plus(settings.DATABASE_PASSWORD)
    db_url = f"postgresql://postgres:{encoded_password}@db.wxuunspyyvqndpodtesy.supabase.co:5432/postgres"
else:
    db_url = settings.DATABASE_URL

# URL 파싱
parsed = urlparse(db_url)

# psycopg3 연결 생성 함수 (prepare_threshold=0으로 prepared statements 비활성화)
def get_connection():
    conn = psycopg.connect(
        host=parsed.hostname,
        port=parsed.port or 5432,
        user=parsed.username,
        password=parsed.password,
        dbname=parsed.path.lstrip('/'),
        sslmode="require",
        prepare_threshold=0  # prepared statements 완전 비활성화
    )
    return conn

# SQLAlchemy 엔진 생성
engine = create_engine(
    "postgresql+psycopg://",
    creator=get_connection,
    poolclass=NullPool,
    echo=True,
)

# 세션 팩토리 생성
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base 클래스 생성 (모든 모델이 상속받을 클래스)
Base = declarative_base()

def get_db():
    """데이터베이스 세션 의존성"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
