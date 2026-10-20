# Chatbot 프로젝트 설명 및 작업 규칙

## 프로젝트 개요

이 프로젝트는 Python 3.12 기반의 FastAPI 챗봇입니다. 브라우저에서 메시지를 보내면 설정된 OpenAI 또는 Anthropic 제공자에 요청하고, 사용자 메시지와 답변을 MongoDB에 저장합니다.

### 구성 요소

- `app/main.py`: FastAPI 애플리케이션, 화면/API 라우트, 로그인 세션, MongoDB 회원·로그인 이력·대화 저장을 관리합니다.
- `app/auth.py`: 가입/로그인 입력을 검증하고 scrypt 비밀번호 해시를 생성·확인합니다.
- `app/config.py`: 프로젝트 루트의 `.env`와 기본값에서 `Settings`를 구성합니다.
- `app/chat_service.py`: OpenAI 또는 Anthropic SDK를 통해 챗봇 응답을 생성합니다.
- `static/site.css`: 랜딩과 계정 화면의 공통 스타일입니다.
- `templates/landing.html`: Chatbot AI 서비스 소개 페이지입니다.
- `templates/signup.html`, `templates/login.html`: 회원가입 및 로그인 화면이며 인증 API를 호출합니다.
- `templates/dashboard.html`: 현재 로그인한 회원의 본인 프로필 화면입니다.
- `templates/index.html`: 로그인한 사용자가 이용하는 브라우저 채팅 화면입니다. `/api/chat`을 호출합니다.
- `tests/test_auth.py`: 회원 입력 및 비밀번호 해시 단위 테스트입니다.
- `tests/test_chat_service.py`: 현재 챗봇 서비스의 단위 테스트입니다.
- `docker-compose.yml`: MongoDB 8 개발 컨테이너를 정의합니다.
- `requirements.txt`, `pyproject.toml`: 각각 pip 설치 목록과 프로젝트 메타데이터/의존성을 정의합니다.

### 주요 동작 및 설정

- 화면 경로: 서비스 메인 `GET /`, 회원가입 `GET /signup`, 로그인 `GET /login`, 회원정보 `GET /dashboard`, 로그인 전용 챗봇 `GET /chat`
- 상태 확인: `GET /health`
- 채팅 API: `POST /api/chat`
- 인증 API: `POST /api/auth/register`, `POST /api/auth/login`, `GET /api/auth/me`, `POST /api/auth/logout`
- API 문서: `/docs`
- MongoDB 기본 주소: `mongodb://localhost:27017`
- MongoDB 기본 데이터베이스와 컬렉션: `abc.users` (회원), `abc.login_logs` (로그인 결과), `abc.chatbot_test` (대화)
- 기본 AI 제공자: OpenAI (`CHAT_PROVIDER=openai`)
- 지원 제공자: `openai`, `anthropic`
- 대화 기록 개수 설정: `CHAT_HISTORY_LIMIT` (1~100)

회원가입 시 이메일은 소문자로 정규화되고 `users.email` 고유 인덱스로 중복 가입을 방지합니다. 비밀번호는 salt가 포함된 scrypt 해시로만 저장하고, API 응답이나 로그인 이력에 넣지 않습니다. 서명된 HttpOnly/SameSite=Lax 세션 쿠키로 로그인 상태를 유지합니다. 세션 키가 없으면 임시 키를 사용하므로 서버 재시작 시 로그인은 만료됩니다. 배포 시 `SESSION_SECRET_KEY`를 지정하고 HTTPS에서 `SESSION_COOKIE_SECURE=true`로 설정하세요.

프로필 화면과 `/api/auth/me`는 현재 로그인한 사용자 본인의 정보만 표시합니다. 챗봇 API는 대화 조회·저장 시 사용자 ID를 함께 확인해 계정별로 기록을 분리합니다. `templates/index.html`은 대화 ID와 제목을 사용자별로 브라우저 `localStorage`에 저장하지만, 저장된 과거 메시지를 재접속 시 화면에 복원하는 API는 없습니다. 실시간 날씨 API도 연동되어 있지 않습니다.

## 작업 규칙

### 변경 전

1. 수정하려는 파일과 직접 연결된 라우트, 설정, 서비스, 템플릿, 테스트를 먼저 읽습니다. 파일명이나 문서만으로 구현 내용을 추정하지 않습니다.
2. 사용자 요청의 범위를 좁고 완전하게 구현합니다. 관련 없는 리팩터링이나 새 의존성 추가는 피합니다.
3. 기존 API 경로, 요청/응답 스키마, MongoDB 데이터 형식, 브라우저 대화 흐름을 변경해야 한다면 관련 사용처와 테스트를 함께 갱신합니다.

### Python 및 FastAPI

1. Python 3.12와 기존 타입·비동기 코드 스타일을 유지합니다.
2. API 입력 검증에는 기존 Pydantic 패턴을 따릅니다. 잘못된 요청을 성공처럼 처리하거나 오류를 조용히 숨기지 않습니다.
3. 외부 AI 제공자 및 MongoDB 오류는 기존 예외 처리 방식에 맞춰 명시적으로 응답하고, 서버 오류에는 필요한 로그를 남깁니다. API 키나 비밀 설정값은 로그에 기록하지 않습니다.
4. MongoDB의 연결 주소, 데이터베이스, 컬렉션은 `Settings`로 설정합니다. 테스트나 개발 과정에서 실제 데이터베이스/컬렉션을 비우거나 삭제하지 않습니다.
5. 새 런타임 패키지를 추가하거나 제거하면 `pyproject.toml`과 `requirements.txt`를 함께 검토하고 일관되게 갱신합니다.
6. 회원 데이터에는 평문 비밀번호를 절대로 저장하지 않습니다. 프로필 응답에는 `password_hash`나 내부 필드를 넣지 않습니다.
7. `/api/auth/me` 및 회원정보 화면은 현재 로그인 계정의 레코드만 반환하며, 사용자 ID 검증 없이 다른 회원을 조회하는 경로를 추가하지 않습니다.
8. 채팅 기록을 읽거나 저장할 때는 항상 대화 ID와 인증된 사용자 ID를 함께 필터에 포함합니다.

### HTML, CSS 및 JavaScript

1. 랜딩·가입·로그인·프로필 UI는 각 `templates/*.html`과 `static/site.css`, 채팅 UI는 `templates/index.html`에 있습니다. 관련 화면과 라우트를 함께 확인합니다.
2. 메시지 본문은 DOM의 `textContent`로 표시하여 사용자 입력을 HTML로 실행하지 않도록 합니다.
3. 비동기 API 요청 중에는 중복 전송을 막고, 서버 오류를 사용자에게 명확히 보여 줍니다.
4. 화면 변경은 데스크톱과 작은 화면 모두에서 확인하고, 라벨·키보드 조작 등 접근성 있는 입력 방식을 유지합니다.
5. 브라우저에서 API를 호출할 때 기존 `/api/chat` 요청·응답 형식과 `conversation_id` 연속 대화 동작을 보존합니다.

### 설정과 비밀 정보

1. 실제 API 키 및 MongoDB 인증 정보는 `.env`에만 보관합니다. `.env` 값을 출력하거나 응답, 문서, 테스트 코드, 로그, 커밋에 복사하지 않습니다.
2. `.env.example`에는 비밀 값을 넣지 않습니다. 설정 항목이 추가되면 실제 값 대신 빈 값 또는 안전한 개발용 기본값을 기록합니다.
3. `.env` 자체는 `.gitignore`에 계속 제외되어 있어야 합니다.
4. 프로젝트는 현재 로컬 개발용 HTTP로 실행됩니다. HTTPS 설정이 추가되지 않았다면 HTTPS가 활성화되었다고 문서화하지 않습니다.

### 테스트 및 검증

1. Python 테스트는 프로젝트 루트에서 다음 명령으로 실행합니다.

   ```powershell
   python -m unittest discover -s tests -v
   ```

2. 관련 화면 변경 시 랜딩·회원가입·로그인 페이지의 HTML, 로그인 전 `/dashboard`와 `/chat` 리다이렉트, 로그인 후 접근을 확인합니다.
3. 라우트/API 변경 시 상태 코드, 요청 검증, 응답 형식, MongoDB 오류/제공자 오류 처리를 가능한 범위에서 테스트합니다.
4. MongoDB나 외부 AI 서비스가 필요한 실제 통합 검증과 mock 기반 단위 테스트를 구분해 결과를 보고합니다. 설정되지 않았거나 연결할 수 없는 외부 서비스를 검증했다고 주장하지 않습니다.
5. 테스트를 실행하지 못했거나 실패한 경우 이를 숨기지 않고, 이유와 남은 검증 항목을 명시합니다.

## 로컬 개발 명령

Windows PowerShell에서 프로젝트 루트 기준으로 사용합니다.

```powershell
py -3.12 -m venv .envtest
.\.envtest\Scripts\Activate.ps1
python -m pip install -r requirements.txt
docker compose up -d mongodb
python -m uvicorn app.main:app --reload
```

브라우저 주소:

- `http://127.0.0.1:8000/`
- `http://127.0.0.1:8000/signup`
- `http://127.0.0.1:8000/login`
- 로그인 후 `http://127.0.0.1:8000/dashboard`
- `http://127.0.0.1:8000/chat`
- `http://127.0.0.1:8000/docs`

테스트 실행:

```powershell
python -m unittest discover -s tests -v
```

## 작업 완료 시 보고

- 변경한 파일과 사용자에게 보이는 동작을 간단히 요약합니다.
- 실행한 테스트와 결과를 정확히 보고합니다.
- 실행하지 않은 통합 테스트나 외부 서비스 검증은 성공한 것처럼 표현하지 않습니다.
- 비밀 정보는 보고 내용에 포함하지 않습니다.
