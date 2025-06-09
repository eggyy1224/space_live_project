import asyncio
import logging
from typing import AsyncIterator, AsyncGenerator

import openai

from core.config import settings

logger = logging.getLogger(__name__)


class RealtimeConversationService:
    """Wrapper around OpenAI real-time conversation API."""

    def __init__(self) -> None:
        self.client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)

    async def stream_conversation(
        self, audio_chunks: AsyncIterator[bytes]
    ) -> AsyncGenerator[bytes, None]:
        """Stream audio chunks to OpenAI and yield TTS audio bytes."""
        try:
            async with self.client.beta.threads.stream(  # type: ignore[attr-defined]
                input_audio=audio_chunks,
            ) as stream:
                async for event in stream:  # pragma: no cover - network
                    if hasattr(event, "audio"):
                        yield event.audio  # type: ignore[attr-defined]
        except Exception as exc:  # pragma: no cover - network
            logger.error("Realtime conversation failed: %s", exc)
            return
