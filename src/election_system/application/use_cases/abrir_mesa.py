from election_system.domain.rules import has_minimum_quorum


class AbrirMesaUseCase:
    async def execute(self, *, mesa_id: str, active_members: int) -> None:
        if not has_minimum_quorum(active_members=active_members):
            msg = f"Mesa {mesa_id} does not meet quorum requirements"
            raise ValueError(msg)

        # TODO: persist asistencia snapshot and replacement decisions.
        # TODO: emit opening event to audit log.
