# FastAPI MongoDB Chatbot

Python 3.12, FastAPI, MongoDB를 사용하는 기본 챗봇 API입니다. OpenAI와 Anthropic 중 하나를 선택할 수 있고, 대화 메시지는 MongoDB에 저장됩니다.

## 준비

1. Python 3.12를 설치합니다.
2. 프로젝트 루트에서 가상 환경을 만들고 활성화합니다.

   ```powershell
   py -3.12 -m venv .envtest
   .\.envtest\Scripts\Activate.ps1
   ```

3. 의존성을 설치합니다.

   ```powershell
   python -m pip install --upgrade pip
   python -m pip install -r requirements.txt
   ```

4. `.env` 파일에 사용할 API 키를 설정합니다. `CHAT_PROVIDER` 값에 따라 해당 키가 필요합니다.

   ```dotenv
   CHAT_PROVIDER=openai
   OPENAI_API_KEY=실제_OpenAI_API_키
   ```

   Anthropic을 사용하려면 `CHAT_PROVIDER=anthropic`으로 바꾸고 `ANTHROPIC_API_KEY`를 설정합니다. 두 키 모두 `.env`에 보관하며, 이 파일은 Git에 포함되지 않습니다.

5. MongoDB를 로컬에서 Docker로 실행합니다.

   ```powershell
   docker compose up -d mongodb
   ```

   이미 실행 중인 MongoDB가 있다면 `MONGODB_URI`를 해당 주소로 바꾸면 됩니다.

## 실행

```powershell
python -m uvicorn app.main:app --reload
```

- 상태 확인: `GET http://127.0.0.1:8000/health`
- 챗봇 화면: `http://127.0.0.1:8000/` 또는 `http://127.0.0.1:8000/chat`
- 대화 API: `POST http://127.0.0.1:8000/api/chat`
- Swagger UI: `http://127.0.0.1:8000/docs`

챗봇 화면은 HTTPS 인증서를 별도로 설정하지 않은 로컬 개발용 HTTP 주소입니다.

요청 예시:

```json
{
  "message": "안녕하세요"
}
```

이어지는 대화에는 응답의 `conversation_id`를 요청에 포함합니다.

```json
{
  "conversation_id": "응답에서_받은_ID",
  "message": "방금 답변을 조금 더 설명해 주세요"
}
```

## 설정

`.env`에서 다음 값을 설정할 수 있습니다.

| 변수 | 기본값 | 설명 |
| --- | --- | --- |
| `CHAT_PROVIDER` | `openai` | `openai` 또는 `anthropic` |
| `MONGODB_URI` | `mongodb://localhost:27017` | MongoDB 연결 주소 |
| `MONGODB_DATABASE` | `abc` | MongoDB 데이터베이스 이름 |
| `MONGODB_COLLECTION` | `chatbot_test` | 대화 메시지를 저장할 컬렉션 이름 |
| `OPENAI_MODEL` | `gpt-4o-mini` | OpenAI 모델 |
| `ANTHROPIC_MODEL` | `claude-haiku-4-5` | Anthropic 모델 |
| `CHAT_HISTORY_LIMIT` | `20` | 모델에 전달할 이전 메시지 수 (1~100) |

`/api/chat`은 간단한 개발용 예제이며 인증 및 사용자별 접근 제어는 포함하지 않습니다. 인터넷에 공개하기 전 인증과 배포 환경에 맞는 보안 설정을 추가하세요.

`abc`는 이 프로젝트에서 사용하는 데이터베이스 이름입니다. MongoDB Compass에서 저장한 연결 표시 이름과는 다르며, MongoDB 인스턴스 주소가 다르면 `.env`의 `MONGODB_URI`도 실제 연결 문자열로 설정해야 합니다.
