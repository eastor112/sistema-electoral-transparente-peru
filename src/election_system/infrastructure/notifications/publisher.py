class NotificationPublisher:
    async def publish(self, *, topic: str, message: dict[str, object]) -> None:
        # TODO: implement provider adapter (NATS/Kafka/Redis streams/WebSocket fanout).
        _ = (topic, message)
