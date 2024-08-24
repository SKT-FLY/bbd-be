from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
import os
from openai import OpenAI
from dotenv import load_dotenv
import re
from app.schemas.intend import CommandRequest, CommandResponseData
from app.crud.result import get_message_by_result
from app.db.session import get_db


router = APIRouter()

# 환경 변수 로드
load_dotenv()

# 환경 변수로 API 키 및 모델 설정
API_KEY_FOR_STANDARDIZATION = os.getenv("OPENAI_API_KEY_FOR_STANDARDIZATION")
API_KEY_FOR_EXTRACT = os.getenv("OPENAI_API_KEY_FOR_EXTRACT")
MODEL_STANDARDIZATION = os.getenv("GPT_4o_MODEL_ALL_DIALECT")
MODEL_EXTRACT = os.getenv("MODEL_EXTRACT")


class TaskManager:
    def __init__(self):
        self.tasks = self.load_tasks_from_env()

    @staticmethod
    def load_tasks_from_env():
        tasks_str = (
            os.getenv("TASKS", "").encode("utf-8").decode("utf-8")
        )  # TASKS 환경 변수를 가져옵니다.
        if tasks_str:
            tasks = tasks_str.split(",")  # 쉼표로 구분된 문자열을 리스트로 변환합니다.
            return [task.strip() for task in tasks]  # 각 작업 앞뒤의 공백을 제거합니다.
        else:
            print(".env 파일에서 TASKS 변수를 찾을 수 없습니다.")
            return []


class TaskProcessor:
    def __init__(self):
        self.client_standardization = OpenAI(api_key=API_KEY_FOR_STANDARDIZATION)
        self.client_extract = OpenAI(api_key=API_KEY_FOR_EXTRACT)
        self.tasks = TaskManager()
        self.tasks_length = len(self.tasks.tasks)
        self.max_tokens = 10

    async def korean_standardization(self, command):
        try:
            command = command.encode("utf-8").decode("utf-8")
            # 메시지를 각 호출마다 새롭게 생성
            messages = [{"role": "user", "content": command}]
            response = self.client_standardization.chat.completions.create(
                model=MODEL_STANDARDIZATION,
                messages=messages
                + [
                    {
                        "role": "system",
                        "content": "다음은 한국어를 소리 나는 대로 적은 것입니다. 만약 이것이 방언이라면 표준어로 바꾸세요.",
                    },
                    {"role": "user", "content": command},
                ],
                temperature=0,
            )
            standardized_response = response.choices[0].message.content
            return standardized_response

        except Exception as e:
            error_message = f"표준어화하는 도중에 에러가 발생함: {e}"
            print(error_message)
            raise HTTPException(status_code=500, detail=f"표준화 실패: {e}")

    async def extract_request(self, command):
        try:
            tasks_string = ", ".join(
                [f"{i+1}. {item}" for i, item in enumerate(self.tasks.tasks)]
            )
            std_command = await self.korean_standardization(command)
            # print(std_command)
            if not std_command:
                return None, "표준화 실패"

            # 메시지를 각 호출마다 새롭게 생성
            messages = [
                {
                    "role": "system",
                    "content": "Q. 다음 중 고객이 원하는 것은? 만약 병원 관련된 답을 선택할 경우, 고객이 어디가 아픈지 확실하지 않다면 8번을 선택할 것. 어딘가로 이동하고 싶은 것으로 추정된다면 9번(택시예약)이 답일 수 있음을 고려할 것.",
                },
                {"role": "user", "content": "내가 비염이 있는 거 같은데"},
                {"role": "system", "content": f"{tasks_string}"},
                {"role": "assistant", "content": "1"},
                {"role": "user", "content": "손자네에 좀 가고 싶어서"},
                {"role": "system", "content": f"{tasks_string}"},
                {"role": "assistant", "content": "9"},
                {"role": "user", "content": std_command},
                {"role": "system", "content": f"{tasks_string}"},
            ]
            response = self.client_extract.chat.completions.create(
                model=MODEL_EXTRACT,
                messages=messages,
                temperature=0,
                max_tokens=self.max_tokens,
            )
            answer = response.choices[0].message.content.strip()

            for i in range(self.tasks_length - 1, -1, -1):
                if re.search(rf"\b{i+1}\b", answer):
                    answer = f"{i+1}"
                    break

            return std_command, answer

        except Exception as e:
            print(f"요청 처리 중 오류 발생: {e}")
            return None, f"오류 발생: {e}"


# 전역적으로 TaskProcessor 인스턴스를 한 번만 생성
processor = TaskProcessor()


@router.post("/process-command")
async def process_command(request: CommandRequest, db: AsyncSession = Depends(get_db)):
    command = request.command
    user_id = request.user_id

    if not command:
        raise HTTPException(status_code=400, detail="No command provided")

    standardized_command, result = await processor.extract_request(command)

    if standardized_command is None:
        raise HTTPException(status_code=500, detail=result)

    # 유저 ID와 result를 기반으로 ResultMessage 조회
    result_message = await get_message_by_result(db, result, user_id)

    if not result_message:
        result_message_text = "Result message not found"
        result_url = ""
    else:
        result_message_text = result_message.message
        result_url = result_message.audio_data

    response_data = CommandResponseData(
        standardized_command=standardized_command,
        result=result,
        message=result_message_text,
        url=result_url,
    )

    return response_data
