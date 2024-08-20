from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from app.db.base import Base
from app.db.session import engine
from app.models import hospital, user, taxi, schedule, text, result_messages
from app.api.v1.endpoints import (
    tts,
    schedule,
    TMAPsearch,
    hospitals,
    taxi_search,
    intend_detection,
    audio,
)

UPLOAD_DIRECTORY = "uploaded_files"


@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        async with engine.begin() as conn:
            # print("Database connection successful!")
            await conn.run_sync(Base.metadata.create_all)
    except Exception as e:
        print(f"Failed to connect to the database: {e}")
    yield


app = FastAPI(lifespan=lifespan)

api_prefix = "/api/v1"
# /files 경로로 요청이 오면 uploaded_files 디렉토리에서 파일을 제공합니다.
app.mount("/files", StaticFiles(directory=UPLOAD_DIRECTORY), name="files")

app.include_router(tts.router, prefix=api_prefix, tags=["TTS"])
app.include_router(schedule.router, prefix=api_prefix, tags=["schedules"])
app.include_router(TMAPsearch.router, prefix=api_prefix, tags=["TMAP"])
app.include_router(hospitals.router, prefix=api_prefix, tags=["hospitals"])
app.include_router(taxi_search.router, prefix=api_prefix, tags=["TMAP"])
app.include_router(intend_detection.router, prefix=api_prefix, tags=["intend"])
app.include_router(audio.router, prefix=api_prefix)
