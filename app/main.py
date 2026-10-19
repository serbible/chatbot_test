import logging
from contextlib import asynccontextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from pydantic import BaseModel, Field, field_validator
from pymongo.errors import PyMongoError

from app.chat_service import (
    ChatService,
    ProviderNotConfiguredError,
    ProviderRequestError,
    ProviderResponseError,
)
from app.config import Settings

logger = logging.getLogger(__name__)
PROJECT_ROOT = Path(__file__).resolve().parent.parent


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

    @asynccontextmanager
    async def lifespan(app: FastAPI):
        mongo_client = AsyncIOMotorClient(configured_settings.mongodb_uri)
        app.state.database = mongo_client[configured_settings.mongodb_database]
        app.state.chat_service = ChatService(configured_settings)
        try:
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

    @app.get("/", include_in_schema=False)
    @app.get("/chat", include_in_schema=False)
    async def chat_page() -> FileResponse:
        return FileResponse(PROJECT_ROOT / "templates" / "index.html")

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
        conversation_id = payload.conversation_id or str(uuid4())
        messages = database[configured_settings.mongodb_collection]

        try:
            previous_messages = await (
                messages.find({"conversation_id": conversation_id})
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
                        "role": "user",
                        "content": payload.message,
                        "created_at": timestamp,
                    },
                    {
                        "conversation_id": conversation_id,
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
