from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import time
from openai import OpenAI, error
from dotenv import load_dotenv
import re

# FastAPI 인스턴스 생성
app = FastAPI()

# 환경 변수 로드
load_dotenv()

# 환경 변수로 API 키 및 모델 설정
API_KEY_FOR_STANDARDIZATION = os.getenv("OPENAI_API_KEY_FOR_STANDARDIZATION")
API_KEY_FOR_EXTRACT = os.getenv("OPENAI_API_KEY_FOR_EXTRACT")
MODEL_STANDARDIZATION = os.getenv("GPT_4o_MODEL_ALL_DIALECT")
MODEL_EXTRACT = os.getenv("MODEL_EXTRACT", "gpt-4o-mini")

class CommandRequest(BaseModel):
    command: str

class TaskProcessor:
    def __init__(self):
        self.client_standardization = OpenAI(api_key=API_KEY_FOR_STANDARDIZATION)
        self.client_extract = OpenAI(api_key=API_KEY_FOR_EXTRACT)
        self.tasks = self.load_tasks('tasks.txt')
        self.tasks_length = len(self.tasks)
        self.max_tokens = 10

    @staticmethod
    def load_tasks(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                tasks = file.read().splitlines()
            return tasks
        except FileNotFoundError:
            print("tasks.txt 파일을 찾을 수 없습니다.")
            return []
        except IOError:
            print("파일을 읽는 중 오류가 발생했습니다.")
            return []

    async def korean_standardization(self, command):
        try:
            # 메시지를 각 호출마다 새롭게 생성
            messages = [{"role": "user", "content": command}]
            response = self.client_standardization.chat.completions.create(
                model=MODEL_STANDARDIZATION,
                messages=messages + [
                    {"role": "system", "content": "다음은 한국어를 소리 나는 대로 적은 것입니다. 만약 이것이 방언이라면 표준어로 바꾸세요."},
                    {"role": "user", "content": command},
                ],
                temperature=0,
            )
            standardized_response = response.choices[0].message.content
            return standardized_response
        
        except error.OpenAIError as e:
            print(f"표준어화하는 도중에 에러가 발생함: {e}")
            return None

    async def extract_request(self, command):
        try:
            tasks_string = ', '.join([f"{i+1}. {item}" for i, item in enumerate(self.tasks)])
            std_command = await self.korean_standardization(command)

            if not std_command:
                return None, "표준화 실패"

            # 메시지를 각 호출마다 새롭게 생성
            messages = [
                {"role": "system", "content": "Q. 다음 중 고객이 원하는 것은? 만약 병원 관련된 답을 선택할 경우, 고객이 어디가 아픈지 확실하지 않다면 7번을 선택할 것. 어딘가로 이동하고 싶은 것으로 추정된다면 8번(택시예약)이 답일 수 있음을 고려할 것."},
                {"role": "user", "content": "내가 비염이 있는 거 같은데"},
                {"role": "system", "content": f"{tasks_string}"},
                {"role": "assistant", "content": "1"},
                {"role": "user", "content": "손자네에 좀 가고 싶어서"},
                {"role": "system", "content": f"{tasks_string}"},
                {"role": "assistant", "content": "8"},
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
                if re.search(rf'\b{i+1}\b', answer):
                    answer = f"{i+1}"
                    break

            return std_command, answer

        except error.OpenAIError as e:
            print(f"요청 처리 중 오류 발생: {e}")
            return None, f"오류 발생: {e}"

# 전역적으로 TaskProcessor 인스턴스를 한 번만 생성
processor = TaskProcessor()

@app.post("/process-command")
async def process_command(request: CommandRequest):
    command = request.command
    
    if not command:
        raise HTTPException(status_code=400, detail="No command provided")
    
    start_time = time.time()
    standardized_command, result = await processor.extract_request(command)
    end_time = time.time()
    
    if standardized_command is None:
        response = {
            'success': False,
            'data': None,
            'error': result
        }
    else:
        response = {
            'success': True,
            'data': {
                'standardized_command': standardized_command,
                'result': result,
                'processing_time': f"{end_time - start_time:.2f} seconds"
            },
            'error': None
        }
    
    return response
