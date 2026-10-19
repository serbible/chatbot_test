# Chatbot 프로젝트 구조 분석

이 문서는 현재 `C:\Chatbot_test` 폴더의 실제 파일을 확인해 정리한 구조 안내입니다. `.env`의 API 키 값은 문서에 포함하지 않았습니다. `.envtest`와 `.venv` 안에는 설치된 Python 패키지 파일이 많이 들어 있어, 트리에는 가상환경의 대표 구성만 표시했습니다.

## 1. 전체 폴더 및 파일 트리

```text
Chatbot_test/
├── .env                         # 로컬 환경변수와 API 키 (비밀 파일)
├── .env.example                 # 환경변수 템플릿
├── .gitignore                   # Git에서 제외할 파일/폴더 규칙
├── README.md                    # 설치·실행·설정 안내
├── chatbot_test_structure.md    # 이 프로젝트 구조 분석 문서
├── docker-compose.yml           # 로컬 MongoDB 실행 설정
├── pyproject.toml               # 패키지 메타데이터와 의존성 설정
├── requirements.txt             # pip 설치용 패키지 목록
├── .envtest/                    # 프로젝트에서 안내하는 Python 가상환경
│   ├── Include/
│   ├── Lib/                     # 설치된 Python 패키지 포함
│   ├── Scripts/
│   └── pyvenv.cfg
├── .venv/                       # 별도로 존재하는 Python 가상환경
│   ├── Lib/
│   ├── Scripts/
│   ├── .gitignore
│   ├── CACHEDIR.TAG
│   └── pyvenv.cfg
├── app/                         # FastAPI 애플리케이션 Python 코드
│   ├── __init__.py              # app 디렉터리를 Python 패키지로 표시
│   ├── chat_service.py          # OpenAI·Anthropic 호출
│   ├── config.py                # 환경변수와 기본 설정
│   ├── main.py                  # FastAPI 앱, 라우트, MongoDB 처리
│   └── __pycache__/             # Python 실행 중 생성되는 캐시
├── templates/                   # 브라우저 화면 HTML
│   └── index.html               # 입력창과 대화 결과를 함께 보여주는 화면
└── tests/                       # 자동 테스트
    ├── test_chat_service.py     # 챗봇 서비스 단위 테스트
    └── __pycache__/             # Python 테스트 실행 중 생성되는 캐시
```

`__pycache__`와 가상환경 내부의 패키지 파일은 설치·실행 과정에서 생성되는 파일입니다. `.gitignore`는 `__pycache__/`, `.envtest/`, `.venv/` 등을 Git 제외 대상으로 지정합니다. 현재 트리의 가상환경 폴더 두 개 중 README의 설치 방법은 `.envtest`를 사용합니다.

## 2. 각 폴더와 파일의 역할

### 폴더

| 경로 | 역할 |
| --- | --- |
| `app/` | FastAPI 앱과 설정, 챗봇 제공자 연동 코드를 보관합니다. |
| `templates/` | FastAPI가 반환하는 HTML 사용자 화면을 보관합니다. |
| `tests/` | 챗봇 서비스 동작을 확인하는 테스트 코드를 보관합니다. |
| `.envtest/` | 프로젝트 안내에서 사용하는 Python 가상환경입니다. |
| `.venv/` | 현재 폴더에 함께 존재하는 별도의 Python 가상환경입니다. |
| `app/__pycache__/`, `tests/__pycache__/` | Python이 실행 중 생성하는 바이트코드 캐시 폴더입니다. |

### 루트 파일

| 파일 | 역할 |
| --- | --- |
| `.env` | 실제 로컬 설정값을 저장합니다. OpenAI·Anthropic 키를 넣는 파일이므로 공유하거나 커밋하지 않습니다. |
| `.env.example` | 키 값은 비워 둔 환경변수 예시입니다. 새 환경의 설정을 시작할 때 참고합니다. |
| `.gitignore` | `.env`, 가상환경, 캐시, 테스트 산출물 등을 Git에서 제외합니다. |
| `README.md` | Python 가상환경 생성, 의존성 설치, MongoDB 실행, 서버 실행 방법을 설명합니다. |
| `chatbot_test_structure.md` | 현재 프로젝트의 구조와 실행 흐름을 설명하는 문서입니다. |
| `docker-compose.yml` | MongoDB 8 컨테이너를 포트 `27017`로 실행하고 데이터를 Docker 볼륨에 보존합니다. |
| `pyproject.toml` | 프로젝트 이름·버전·Python 요구 버전·런타임 및 개발 의존성을 선언합니다. |
| `requirements.txt` | `pip install -r requirements.txt`에서 사용하는 FastAPI, MongoDB 드라이버, 제공자 SDK 및 테스트 패키지 목록입니다. |

### 애플리케이션 및 테스트 파일

| 파일 | 역할 |
| --- | --- |
| `app/__init__.py` | 비어 있는 파일로, `app`을 Python 패키지로 인식시킵니다. |
| `app/config.py` | Pydantic Settings로 `.env`와 기본 설정을 읽습니다. |
| `app/chat_service.py` | 선택된 AI 제공자에 요청하고 답변 텍스트를 반환합니다. |
| `app/main.py` | FastAPI 앱 생성, HTML/API 라우트, MongoDB 수명주기와 대화 저장을 담당합니다. |
| `templates/index.html` | CSS와 JavaScript가 포함된 단일 챗봇 웹 페이지입니다. |
| `tests/test_chat_service.py` | OpenAI 키 누락 처리 및 대화 기록을 포함한 요청 구성을 검사합니다. |

## 3. 주요 Python 파일의 기능 및 실행 흐름

### `app/config.py`

`Settings` 클래스가 프로젝트 루트의 `.env`를 읽습니다. 코드에서 정의한 기본값은 다음과 같습니다.

| 설정 | 기본값 |
| --- | --- |
| `CHAT_PROVIDER` | `openai` |
| `MONGODB_URI` | `mongodb://localhost:27017` |
| `MONGODB_DATABASE` | `abc` |
| `MONGODB_COLLECTION` | `chatbot_test` |
| `OPENAI_MODEL` | `gpt-4o-mini` |
| `ANTHROPIC_MODEL` | `claude-haiku-4-5` |
| `CHAT_HISTORY_LIMIT` | `20` (허용 범위 1~100) |
| 시스템 프롬프트 | `You are a helpful assistant.` |

OpenAI와 Anthropic API 키는 설정값으로 읽지만 기본 키 값은 설정 코드에 들어 있지 않습니다. 실제 키는 로컬 `.env`에 지정해야 합니다.

### `app/main.py`

- `create_app()`이 설정을 받아 FastAPI 앱을 만듭니다. 설정을 전달하지 않으면 `Settings()`를 사용합니다.
- 앱 시작(lifespan) 시 MongoDB 클라이언트와 `ChatService`를 생성하고, 종료 시 서비스 클라이언트를 닫은 뒤 MongoDB 클라이언트를 닫습니다.
- `GET /`와 `GET /chat`은 `templates/index.html` 파일을 반환합니다.
- `GET /health`는 MongoDB `ping` 명령으로 연결 상태를 확인합니다.
- `POST /api/chat`은 메시지와 선택적 대화 ID를 받습니다. 새 대화에는 UUID를 생성합니다.
- 지정된 컬렉션에서 해당 대화의 최근 기록을 읽어 시간순으로 정리한 후 `ChatService`에 전달합니다.
- 답변을 받으면 사용자 메시지와 어시스턴트 답변을 UTC 생성 시각과 함께 MongoDB에 저장합니다.
- 제공자 설정 누락, 제공자 요청/응답 실패, MongoDB 오류를 각각 HTTP 오류 응답으로 처리합니다.
- 모듈 끝에서 `app = create_app()`을 생성하며, Uvicorn은 이 앱 객체를 실행합니다.

### `app/chat_service.py`

`ChatService`는 설정된 `CHAT_PROVIDER` 값에 따라 `AsyncOpenAI` 또는 `AsyncAnthropic` 클라이언트를 만듭니다. 대화 기록과 새 사용자 메시지를 선택된 제공자 SDK 형식으로 보내고, 답변 텍스트만 반환합니다. 키가 없거나 요청 실패 또는 빈 응답인 경우 전용 예외를 발생시킵니다. 제공자 SDK 클라이언트도 `close()`에서 정리합니다.

### 요청부터 저장까지의 실행 흐름

```text
브라우저(templates/index.html)
  └─ POST /api/chat { message, conversation_id? }
       └─ app/main.py: ChatRequest 검증 및 대화 ID 결정
            ├─ MongoDB abc.chatbot_test에서 최근 대화 읽기
            ├─ app/chat_service.py: OpenAI 또는 Anthropic에 요청
            ├─ MongoDB에 사용자 질문과 답변 저장
            └─ { conversation_id, reply } 응답
                 └─ 브라우저 대화 영역에 질문과 답변 표시
```

화면은 현재 대화 ID와 제목을 브라우저 `localStorage`에 보관하고, 새 대화 버튼으로 이를 지웁니다. 이 HTML 코드에는 페이지를 다시 열었을 때 MongoDB에서 기존 메시지를 불러오는 별도 API 호출은 구현되어 있지 않습니다.

## 4. 주요 라이브러리와 설정 파일 설명

### 주요 라이브러리

실제 의존성 범위는 `pyproject.toml` 및 `requirements.txt`에 선언되어 있습니다.

| 라이브러리 | 사용 목적 |
| --- | --- |
| FastAPI | HTTP 라우트와 요청·응답 검증을 갖춘 웹 API |
| Uvicorn | ASGI 서버. 개발 실행 명령으로 사용합니다. |
| Motor | FastAPI 비동기 코드에서 MongoDB 작업을 수행하는 클라이언트입니다. |
| PyMongo | MongoDB 예외 타입을 처리하고 Motor의 MongoDB 기능을 제공합니다. |
| Pydantic | 요청 데이터 검증과 설정 모델에 사용합니다. |
| pydantic-settings | 환경변수와 `.env` 설정을 `Settings`로 읽습니다. |
| OpenAI Python SDK | OpenAI 채팅 완성 API를 비동기로 호출합니다. |
| Anthropic Python SDK | Anthropic 메시지 API를 비동기로 호출합니다. |
| httpx | 테스트 클라이언트 지원 의존성입니다. |
| pytest | 테스트 실행 도구로 의존성 목록에 포함되어 있습니다. 실제 테스트 파일은 표준 라이브러리 `unittest`를 사용합니다. |

### 설정 파일

- `pyproject.toml`: Python `>=3.12,<3.13` 요구 사항과 프로젝트 런타임 패키지, 선택적 개발 패키지를 정의합니다.
- `requirements.txt`: 설치 명령에서 사용하는 패키지 목록입니다. 런타임 패키지뿐 아니라 `httpx`, `pytest`도 포함합니다.
- `.env`: 개발 환경의 실제 API 키와 접속 설정을 둡니다. 비밀 값은 이 문서에 기록하지 않습니다.
- `.env.example`: `.env`에서 사용할 수 있는 변수 이름과 기본 설정의 예를 제공합니다.
- `docker-compose.yml`: 로컬 MongoDB 서비스와 데이터 저장 볼륨을 정의합니다.
- `.gitignore`: 비밀 설정과 가상환경, Python 캐시 등을 버전 관리에서 제외합니다.

## 5. 프로젝트 실행 방법

아래 명령은 Windows PowerShell 기준이며, 프로젝트 루트(`C:\Chatbot_test`)에서 실행합니다.

1. Python 3.12 가상환경을 만들고 활성화합니다.

   ```powershell
   py -3.12 -m venv .envtest
   .\.envtest\Scripts\Activate.ps1
   ```

   이미 만들어진 `.envtest`를 사용할 때는 생성 명령을 생략하고 활성화하면 됩니다.

2. 필요한 패키지를 설치합니다.

   ```powershell
   python -m pip install -r requirements.txt
   ```

3. `.env`에서 `CHAT_PROVIDER`와 해당 제공자의 API 키를 설정합니다. OpenAI를 사용하는 경우 `OPENAI_API_KEY`, Anthropic을 사용하는 경우 `ANTHROPIC_API_KEY`가 필요합니다. 키 값은 안전하게 관리하고 공유하지 마세요.

4. 로컬 MongoDB를 Docker로 실행합니다.

   ```powershell
   docker compose up -d mongodb
   ```

   기본 MongoDB URI는 `mongodb://localhost:27017`이고, 앱은 데이터베이스 `abc`와 컬렉션 `chatbot_test`를 사용합니다. 외부 MongoDB를 사용하는 경우 `.env`의 `MONGODB_URI`를 해당 연결 URI로 설정합니다.

5. 개발 서버를 실행합니다.

   ```powershell
   python -m uvicorn app.main:app --reload
   ```

6. 브라우저에서 화면을 열고 테스트합니다.

   - 챗봇 화면: `http://127.0.0.1:8000/` 또는 `http://127.0.0.1:8000/chat`
   - Swagger API 문서: `http://127.0.0.1:8000/docs`
   - 데이터베이스 상태: `http://127.0.0.1:8000/health`

7. 테스트는 프로젝트 루트에서 실행할 수 있습니다.

   ```powershell
   python -m unittest discover -s tests -v
   ```

현재 README는 이 앱을 로컬 개발용 HTTP 서버로 안내합니다. HTTPS 인증서 설정은 프로젝트에 포함되어 있지 않습니다.

## 6. 파일 간의 의존 관계

```text
pyproject.toml / requirements.txt
  └─ FastAPI, Motor/PyMongo, 제공자 SDK, Pydantic Settings 설치

.env ───────────────┐
                    └─ app/config.py: Settings
                         ├─ app/main.py
                         │    ├─ FastAPI 라우트와 lifespan
                         │    ├─ MongoDB 접속 및 대화 저장
                         │    └─ templates/index.html 반환
                         └─ app/chat_service.py
                              └─ OpenAI 또는 Anthropic SDK 호출

templates/index.html
  └─ 브라우저에서 POST /api/chat 요청
       └─ app/main.py ── app/chat_service.py ── AI 제공자 API
                 └─ MongoDB의 abc.chatbot_test 컬렉션

tests/test_chat_service.py
  ├─ app/chat_service.py
  └─ app/config.py
```

구체적으로 `app/main.py`는 `app.config.Settings`와 `app.chat_service.ChatService`를 가져옵니다. `app/chat_service.py`도 `Settings`를 가져와 제공자와 모델을 선택합니다. HTML은 정적 파일 서버나 별도 JavaScript 빌드 도구를 사용하지 않고, `main.py` 라우트에서 직접 반환되며 자체 JavaScript의 `fetch("/api/chat")`로 API와 통신합니다. 테스트는 실제 제공자 API를 호출하지 않고 OpenAI 요청 부분을 mock 처리합니다.

## 7. 초보자를 위한 전체 프로젝트 구조 요약

- `templates/index.html`은 사용자가 보는 채팅 화면입니다.
- `app/main.py`는 화면 주소, 채팅 API, MongoDB 저장을 연결하는 앱의 중심입니다.
- `app/config.py`는 `.env`에서 제공자 선택, 키, MongoDB 주소 같은 설정을 읽습니다.
- `app/chat_service.py`는 실제 AI 제공자(OpenAI 또는 Anthropic)에 질문을 전달하고 답변을 받습니다.
- MongoDB는 질문과 답변의 대화 기록을 `abc` 데이터베이스의 `chatbot_test` 컬렉션에 저장합니다.
- `tests/`에는 서비스의 일부 동작을 빠르게 확인하는 테스트가 있습니다.
- `requirements.txt`는 패키지 설치 목록이며, `docker-compose.yml`은 개발용 MongoDB를 실행하는 설정입니다.
- 처음 실행할 때는 Python 3.12 가상환경을 활성화하고 패키지를 설치한 뒤, `.env`에 사용할 API 키를 넣고 MongoDB와 Uvicorn 서버를 실행하면 됩니다.
- 현재 구조에는 사용자 인증, 날씨 조회 API, MongoDB 대화 기록을 화면에 다시 불러오는 기능은 확인되지 않았으므로, 문서에서 구현된 기능으로 간주하지 않습니다.
