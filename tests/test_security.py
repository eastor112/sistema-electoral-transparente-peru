from election_system.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    generate_otp_code,
    hash_otp_code,
    hash_password,
    verify_password,
)


def test_password_hash_and_verify() -> None:
    password = "S3gura-Password-123"
    hashed = hash_password(password)

    assert hashed.startswith("pbkdf2_sha256$")
    assert verify_password(password, hashed)
    assert not verify_password("wrong-password", hashed)


def test_access_and_refresh_tokens_have_expected_type() -> None:
    access_token = create_access_token("user-123")
    refresh_token = create_refresh_token("user-123")

    access_payload = decode_token(access_token, expected_type="access")
    refresh_payload = decode_token(refresh_token, expected_type="refresh")

    assert access_payload["sub"] == "user-123"
    assert access_payload["type"] == "access"
    assert refresh_payload["sub"] == "user-123"
    assert refresh_payload["type"] == "refresh"


def test_generate_otp_code_and_hash_is_stable() -> None:
    code = generate_otp_code()

    assert code.isdigit()
    assert len(code) == 6
    assert hash_otp_code(code) == hash_otp_code(code)
