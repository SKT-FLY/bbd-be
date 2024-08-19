from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

# 데이터베이스 URL
SQLALCHEMY_DATABASE_URL = os.environ.get("DATABASE_URL")

# 비동기 SQLAlchemy 엔진을 생성
engine = create_async_engine(
    SQLALCHEMY_DATABASE_URL,
    echo=True,
    pool_recycle=28000,  # 28000초 후에 연결 재설정
    connect_args={"connect_timeout": 20},  # 연결 시도 시 타임아웃 설정
)

# 비동기 세션을 설정
SessionLocal = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, class_=AsyncSession
)


# 비동기 데이터베이스 세션을 생성하고 제공하는 함수
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()
