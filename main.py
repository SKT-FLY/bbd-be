from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.base import Base
from app.db.session import engine
from app.models import hospital, user, taxi, schedule
from app.api.v1.endpoints import tts, schedule, TMAPsearch


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

app.include_router(tts.router, prefix=api_prefix)
app.include_router(schedule.router, prefix=api_prefix, tags=["schedules"])
app.include_router(TMAPsearch.router, prefix=api_prefix, tags=["TMAP"])
