from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.db.base import Base
from app.db.session import engine
from app.models import hospital, user, taxi, schedule


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


@app.get("/")
async def hello():
    return "Hello World"
