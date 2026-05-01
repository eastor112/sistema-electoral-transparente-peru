class NotificationService:
    async def broadcast(self, *, channel: str, payload: dict[str, object]) -> None:
        # TODO: publish event to notification bus (websocket/sse/queue).
        _ = (channel, payload)
