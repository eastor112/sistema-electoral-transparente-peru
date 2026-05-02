import httpx

from election_system.application.ports import TelegramSenderPort
from election_system.core.config import settings


class ConsoleTelegramSender(TelegramSenderPort):
    async def send_message(self, *, chat_id: str, text: str) -> None:
        print("=== TELEGRAM (console provider) ===")
        print(f"Chat ID: {chat_id}")
        print("Message:")
        print(text)
        print("=== END TELEGRAM ===")


class TelegramBotSender(TelegramSenderPort):
    async def send_message(self, *, chat_id: str, text: str) -> None:
        if not settings.telegram_bot_token:
            raise RuntimeError("telegram_bot_token is required when using telegram bot provider")

        url = (
            f"{settings.telegram_api_base_url}/bot{settings.telegram_bot_token}/sendMessage"
        )
        payload = {
            "chat_id": chat_id,
            "text": text,
        }

        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(url, json=payload)
        response.raise_for_status()


def build_telegram_sender() -> TelegramSenderPort:
    if settings.app_env.lower() in {"dev", "local", "development"}:
        return ConsoleTelegramSender()

    provider = settings.telegram_provider.lower()
    if provider == "console":
        return ConsoleTelegramSender()
    if provider == "bot":
        return TelegramBotSender()

    raise RuntimeError(f"Unsupported telegram_provider: {settings.telegram_provider}")
