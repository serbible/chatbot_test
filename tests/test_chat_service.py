import unittest
from unittest.mock import AsyncMock, Mock

from app.chat_service import ChatService, ProviderNotConfiguredError
from app.config import Settings


class ChatServiceTests(unittest.IsolatedAsyncioTestCase):
    async def test_openai_provider_requires_api_key(self) -> None:
        service = ChatService(
            Settings(chat_provider="openai", openai_api_key="")
        )

        with self.assertRaises(ProviderNotConfiguredError):
            await service.reply([], "hello")

    async def test_openai_provider_includes_history(self) -> None:
        service = ChatService(
            Settings(chat_provider="openai", openai_api_key="test-key")
        )
        create = AsyncMock(
            return_value=Mock(
                choices=[Mock(message=Mock(content="Hello back."))]
            )
        )
        service.openai_client.chat.completions.create = create

        reply = await service.reply(
            [{"role": "user", "content": "Hi"}], "How are you?"
        )

        self.assertEqual(reply, "Hello back.")
        self.assertEqual(
            create.await_args.kwargs["messages"],
            [
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hi"},
                {"role": "user", "content": "How are you?"},
            ],
        )


if __name__ == "__main__":
    unittest.main()
