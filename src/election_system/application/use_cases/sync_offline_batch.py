class SyncOfflineBatchUseCase:
    async def execute(self, *, mesa_id: str, batch_id: str) -> None:
        # TODO: validate sequence ordering and idempotency keys.
        # TODO: persist events atomically and publish outbox messages.
        # TODO: update sync state and reliability score factors.
        _ = (mesa_id, batch_id)
