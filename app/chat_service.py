from collections.abc import Sequence
from typing import Any

import anthropic
from openai import AsyncOpenAI, OpenAIError
from anthropic import AsyncAnthropic

from app.config import Settings


class ProviderNotConfiguredError(Exception):
    pass


class ProviderRequestError(Exception):
    pass


class ProviderResponseError(Exception):
    pass


class ChatService:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.openai_client = (
            AsyncOpenAI(api_key=settings.openai_api_key)
            if settings.chat_provider == "openai" and settings.openai_api_key
            else None
        )
        self.anthropic_client = (
            AsyncAnthropic(api_key=settings.anthropic_api_key)
            if settings.chat_provider == "anthropic" and settings.anthropic_api_key
            else None
        )

    async def reply(
        self, history: Sequence[dict[str, Any]], user_message: str
    ) -> str:
        if self.settings.chat_provider == "openai":
            return await self._reply_with_openai(history, user_message)
        return await self._reply_with_anthropic(history, user_message)

    async def _reply_with_openai(
        self, history: Sequence[dict[str, Any]], user_message: str
    ) -> str:
        if self.openai_client is None:
            raise ProviderNotConfiguredError(
                "Set OPENAI_API_KEY to use the OpenAI provider."
            )

        try:
            response = await self.openai_client.chat.completions.create(
                model=self.settings.openai_model,
                messages=[
                    {"role": "system", "content": self.settings.system_prompt},
                    *[
                        {"role": item["role"], "content": item["content"]}
                        for item in history
                    ],
                    {"role": "user", "content": user_message},
                ],
            )
        except OpenAIError as exc:
            raise ProviderRequestError("The OpenAI request failed.") from exc

        answer = response.choices[0].message.content
        if not answer:
            raise ProviderResponseError("OpenAI returned an empty response.")
        return answer

    async def _reply_with_anthropic(
        self, history: Sequence[dict[str, Any]], user_message: str
    ) -> str:
        if self.anthropic_client is None:
            raise ProviderNotConfiguredError(
                "Set ANTHROPIC_API_KEY to use the Anthropic provider."
            )

        try:
            response = await self.anthropic_client.messages.create(
                model=self.settings.anthropic_model,
                max_tokens=1024,
                system=self.settings.system_prompt,
                messages=[
                    *[
                        {"role": item["role"], "content": item["content"]}
                        for item in history
                    ],
                    {"role": "user", "content": user_message},
                ],
            )
        except anthropic.APIError as exc:
            raise ProviderRequestError("The Anthropic request failed.") from exc

        answer = "".join(
            block.text for block in response.content if block.type == "text"
        )
        if not answer:
            raise ProviderResponseError("Anthropic returned an empty response.")
        return answer

    async def close(self) -> None:
        if self.openai_client is not None:
            await self.openai_client.close()
        if self.anthropic_client is not None:
            await self.anthropic_client.close()
