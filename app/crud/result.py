from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from app.models.result_messages import ResultMessage


async def get_message_by_result(db: AsyncSession, result: str) -> ResultMessage:
    """
    result 문자열을 기준으로 데이터베이스에서 ResultMessage를 비동기적으로 조회합니다.
    """
    stmt = select(ResultMessage).where(ResultMessage.result == result)
    result = await db.execute(stmt)
    return result.scalars().first()
