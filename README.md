# FastAPI MongoDB Chatbot

Python 3.12, FastAPI, MongoDB를 사용하는 기본 챗봇 API입니다. OpenAI와 Anthropic 중 하나를 선택할 수 있고, 대화 메시지는 MongoDB에 저장됩니다.

## 주요 기능

- OpenAI 또는 Anthropic을 선택해 비동기로 챗봇 응답 생성
- 브라우저 채팅 화면과 JSON 채팅 API 제공
- MongoDB에 대화 기록을 저장하고 후속 질문을 위해 최근 기록을 조회
- MongoDB 연결 상태 확인 endpoint 제공
- Pydantic 기반 환경 설정 및 요청 검증

실시간 날씨 조회, 사용자 인증, MongoDB 대화 기록을 브라우저에 다시 표시하는 기능은 포함되어 있지 않습니다.

## 프로젝트 구조

```text
Chatbot_test/
├── app/
│   ├── __init__.py
│   ├── chat_service.py       # OpenAI·Anthropic 연동
│   ├── config.py             # .env 및 애플리케이션 설정
│   └── main.py               # FastAPI 라우트와 MongoDB 저장
├── templates/
│   └── index.html            # 브라우저 채팅 화면
├── tests/
│   └── test_chat_service.py  # 챗봇 서비스 단위 테스트
├── .env.example              # 비밀 값이 포함되지 않은 설정 예시
├── .gitignore
├── docker-compose.yml        # 로컬 MongoDB 실행 설정
├── pyproject.toml            # 프로젝트 메타데이터 및 의존성
├── requirements.txt          # pip 설치 목록
└── README.md
```

추가 문서로 `chatbot_test_structure.md`(상세 파일 구조 분석), `chatbot_test_claude.md`(프로젝트 설명 및 작업 규칙), `chatbot_test_export.md`(대화 내보내기), `chatbot_test_export.docx`(Word 문서)가 있습니다. 이 문서들은 공개 저장소에 포함해도 되는지 업로드 전에 확인하세요.

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

4. `.env.example`을 참고해 루트에 `.env` 파일을 만들고 사용할 API 키를 설정합니다. `CHAT_PROVIDER` 값에 따라 해당 키가 필요합니다. `.env`에는 비밀 값이 있으므로 GitHub에 업로드하지 않습니다.

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

실행 중인 서버는 터미널에서 `Ctrl+C`를 눌러 종료합니다.

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

## 테스트

```powershell
python -m unittest discover -s tests -v
```

## GitHub 업로드 전 보안 확인

- `.env`, API 키, 비밀번호, MongoDB 인증 정보가 문서·코드·로그에 포함되지 않았는지 확인합니다.
- `.gitignore`는 비밀 파일, 가상환경, 캐시 및 로컬 산출물을 제외합니다. 이미 Git에서 추적 중인 파일은 `.gitignore`에 추가해도 자동으로 추적 해제되지 않으므로 `git status`로 확인해야 합니다.
- 대화 내보내기 문서에는 대화 내용이 포함될 수 있으니 공유해도 되는 내용인지 검토한 뒤 업로드합니다.
