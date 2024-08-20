from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update
from app.models.result_messages import ResultMessage


async def update_audio_data(db: AsyncSession, id: int, file_location: str):
    stmt = (
        update(ResultMessage)
        .where(ResultMessage.id == id)
        .values(audio_data=file_location)
    )
    await db.execute(stmt)
    await db.commit()
