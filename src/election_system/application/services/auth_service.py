from election_system.core.security import create_access_token


class AuthService:
    async def login(self, *, actor_identifier: str) -> str:
        # TODO: validate credentials/identity assertions and actor state.
        return create_access_token(subject=actor_identifier)
