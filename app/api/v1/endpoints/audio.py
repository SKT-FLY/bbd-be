import aiofiles
from pathlib import Path
from fastapi import APIRouter, File, UploadFile, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.crud.upload import update_audio_data

UPLOAD_DIRECTORY = "uploaded_files"
Path(UPLOAD_DIRECTORY).mkdir(parents=True, exist_ok=True)

router = APIRouter()


@router.put("/update-audio/{id}")
async def update_audio(
    id: int, file: UploadFile = File(...), db: AsyncSession = Depends(get_db)
):
    # 비동기적으로 파일을 서버의 지정된 디렉토리에 저장
    file_location = Path(UPLOAD_DIRECTORY) / file.filename
    async with aiofiles.open(file_location, "wb") as buffer:
        while content := await file.read(1024):  # 1024 bytes씩 읽어옴
            await buffer.write(content)

    # 데이터베이스의 특정 레코드의 audio_data 필드 업데이트
    await update_audio_data(db, id, str(file_location))

    return {"id": id, "file_location": str(file_location)}
