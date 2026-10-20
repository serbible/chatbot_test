import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
import secrets
from typing import Any
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, EmailStr, Field, field_validator
from bson import ObjectId
from pymongo.errors import DuplicateKeyError, PyMongoError
from starlette.middleware.sessions import SessionMiddleware

from app.auth import LoginRequest, RegisterRequest, hash_password, verify_password
from app.chat_service import (
    ChatService,
    ProviderNotConfiguredError,
    ProviderRequestError,
    ProviderResponseError,
)
from app.config import Settings

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class UserResponse(BaseModel):
    id: str
    name: str
    email: EmailStr
    created_at: datetime


class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=8000)
    conversation_id: str | None = Field(default=None, min_length=1, max_length=64)

    @field_validator("message")
    @classmethod
    def message_must_not_be_blank(cls, value: str) -> str:
        cleaned = value.strip()
        if not cleaned:
            raise ValueError("Message must not be blank.")
        return cleaned


class ChatResponse(BaseModel):
    conversation_id: str
    reply: str


def create_app(settings: Settings | None = None) -> FastAPI:
    configured_settings = settings or Settings()
    session_secret = configured_settings.session_secret_key
    if not session_secret:
        session_secret = secrets.token_urlsafe(48)
        logger.warning(
            "SESSION_SECRET_KEY is unset; sessions will be invalidated on restart."
        )

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        mongo_client = AsyncIOMotorClient(configured_settings.mongodb_uri)
        app.state.database = mongo_client[configured_settings.mongodb_database]
        app.state.chat_service = ChatService(configured_settings)
        try:
            await app.state.database["users"].create_index("email", unique=True)
            await app.state.database["login_logs"].create_index(
                [("user_id", 1), ("created_at", -1)]
            )
            yield
        finally:
            await app.state.chat_service.close()
            mongo_client.close()

    app = FastAPI(
        title="FastAPI MongoDB Chatbot",
        description="A simple chatbot API using OpenAI or Anthropic and MongoDB.",
        version="0.1.0",
        lifespan=lifespan,
    )
    app.add_middleware(
        SessionMiddleware,
        secret_key=session_secret,
        session_cookie="chatbot_session",
        max_age=configured_settings.session_max_age_seconds,
        same_site="lax",
        https_only=configured_settings.session_cookie_secure,
    )

    @app.get("/", include_in_schema=False)
    async def landing_page() -> FileResponse:
        return FileResponse(PROJECT_ROOT / "templates" / "landing.html")

    @app.get("/signup", include_in_schema=False)
    async def signup_page() -> FileResponse:
        return FileResponse(PROJECT_ROOT / "templates" / "signup.html")

    @app.get("/login", include_in_schema=False)
    async def login_page() -> FileResponse:
        return FileResponse(PROJECT_ROOT / "templates" / "login.html")

    async def get_current_user(request: Request) -> dict[str, Any]:
        user_id = request.session.get("user_id")
        if not isinstance(user_id, str):
            raise HTTPException(status_code=401, detail="Login required.")

        if not ObjectId.is_valid(user_id):
            request.session.clear()
            raise HTTPException(status_code=401, detail="Login required.")

        try:
            user = await request.app.state.database["users"].find_one(
                {"_id": ObjectId(user_id)}
            )
        except PyMongoError as exc:
            logger.exception("Could not load the authenticated user.")
            raise HTTPException(
                status_code=503, detail="Account service is unavailable."
            ) from exc

        if user is None:
            request.session.clear()
            raise HTTPException(status_code=401, detail="Login required.")
        return user

    def user_response(user: dict[str, Any]) -> UserResponse:
        return UserResponse(
            id=str(user["_id"]),
            name=user["name"],
            email=user["email"],
            created_at=user["created_at"],
        )

    @app.get("/dashboard", include_in_schema=False)
    async def dashboard_page(request: Request):
        try:
            await get_current_user(request)
        except HTTPException as exc:
            if exc.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise
        return FileResponse(PROJECT_ROOT / "templates" / "dashboard.html")

    @app.get("/chat", include_in_schema=False)
    async def chat_page(request: Request):
        try:
            await get_current_user(request)
        except HTTPException as exc:
            if exc.status_code == 401:
                return RedirectResponse("/login", status_code=303)
            raise
        return FileResponse(PROJECT_ROOT / "templates" / "index.html")

    @app.post("/api/auth/register", response_model=UserResponse, status_code=201)
    async def register(payload: RegisterRequest, request: Request) -> UserResponse:
        user = {
            "name": payload.name,
            "email": str(payload.email),
            "password_hash": hash_password(payload.password),
            "created_at": datetime.now(timezone.utc),
        }
        try:
            result = await request.app.state.database["users"].insert_one(user)
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=409, detail="An account with this email already exists."
            ) from exc
        except PyMongoError as exc:
            logger.exception("Account registration failed.")
            raise HTTPException(
                status_code=503, detail="Account service is unavailable."
            ) from exc

        user["_id"] = result.inserted_id
        request.session.clear()
        request.session["user_id"] = str(result.inserted_id)
        return user_response(user)

    @app.post("/api/auth/login", response_model=UserResponse)
    async def login(payload: LoginRequest, request: Request) -> UserResponse:
        database = request.app.state.database
        email = str(payload.email)
        try:
            user = await database["users"].find_one({"email": email})
            if user is None:
                hash_password(payload.password)
                authenticated = False
            else:
                authenticated = verify_password(
                    payload.password, user.get("password_hash", "")
                )

            await database["login_logs"].insert_one(
                {
                    "user_id": user["_id"] if user is not None else None,
                    "email": email,
                    "succeeded": authenticated,
                    "created_at": datetime.now(timezone.utc),
                }
            )
        except PyMongoError as exc:
            logger.exception("Account login operation failed.")
            raise HTTPException(
                status_code=503, detail="Account service is unavailable."
            ) from exc

        if not authenticated or user is None:
            raise HTTPException(
                status_code=401, detail="Email or password is incorrect."
            )

        request.session.clear()
        request.session["user_id"] = str(user["_id"])
        return user_response(user)

    @app.get("/api/auth/me", response_model=UserResponse)
    async def current_user(request: Request) -> UserResponse:
        return user_response(await get_current_user(request))

    @app.post("/api/auth/logout")
    async def logout(request: Request) -> dict[str, str]:
        request.session.clear()
        return {"status": "logged_out"}

    app.mount(
        "/static",
        StaticFiles(directory=PROJECT_ROOT / "static"),
        name="static",
    )

    @app.get("/health")
    async def health(request: Request) -> dict[str, str]:
        try:
            await request.app.state.database.command("ping")
        except PyMongoError as exc:
            logger.exception("MongoDB health check failed.")
            raise HTTPException(
                status_code=503,
                detail="MongoDB is unavailable.",
            ) from exc
        return {"status": "ok", "database": "connected"}

    @app.post("/api/chat", response_model=ChatResponse)
    async def chat(payload: ChatRequest, request: Request) -> ChatResponse:
        database: AsyncIOMotorDatabase = request.app.state.database
        user = await get_current_user(request)
        user_id = str(user["_id"])
        conversation_id = payload.conversation_id or str(uuid4())
        messages = database[configured_settings.mongodb_collection]

        try:
            previous_messages = await (
                messages.find(
                    {"conversation_id": conversation_id, "user_id": user_id}
                )
                .sort("created_at", -1)
                .limit(configured_settings.chat_history_limit)
                .to_list(length=configured_settings.chat_history_limit)
            )
            previous_messages.reverse()
            history = [
                {"role": item["role"], "content": item["content"]}
                for item in previous_messages
            ]
            reply = await request.app.state.chat_service.reply(
                history, payload.message
            )
            timestamp = datetime.now(timezone.utc)
            await messages.insert_many(
                [
                    {
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "role": "user",
                        "content": payload.message,
                        "created_at": timestamp,
                    },
                    {
                        "conversation_id": conversation_id,
                        "user_id": user_id,
                        "role": "assistant",
                        "content": reply,
                        "created_at": timestamp,
                    },
                ]
            )
        except ProviderNotConfiguredError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
        except ProviderRequestError as exc:
            logger.exception("Chat provider request failed.")
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except ProviderResponseError as exc:
            logger.exception("Chat provider returned an invalid response.")
            raise HTTPException(status_code=502, detail=str(exc)) from exc
        except PyMongoError as exc:
            logger.exception("MongoDB chat operation failed.")
            raise HTTPException(
                status_code=503,
                detail="Could not read or save the conversation.",
            ) from exc

        return ChatResponse(conversation_id=conversation_id, reply=reply)

    return app


app = create_app()
