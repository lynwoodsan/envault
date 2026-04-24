"""Tests for envault.crypto encryption/decryption utilities."""

import pytest
from envault.crypto import encrypt, decrypt


PASSWORD = "super-secret-passphrase"
PLAINTEXT = "DATABASE_URL=postgres://user:pass@localhost/mydb"


def test_encrypt_returns_string():
    token = encrypt(PLAINTEXT, PASSWORD)
    assert isinstance(token, str)
    assert len(token) > 0


def test_encrypt_produces_unique_ciphertexts():
    """Each call should produce a different ciphertext due to random salt/nonce."""
    token1 = encrypt(PLAINTEXT, PASSWORD)
    token2 = encrypt(PLAINTEXT, PASSWORD)
    assert token1 != token2


def test_decrypt_roundtrip():
    token = encrypt(PLAINTEXT, PASSWORD)
    result = decrypt(token, PASSWORD)
    assert result == PLAINTEXT


def test_decrypt_wrong_password_raises():
    token = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError, match="Decryption failed"):
        decrypt(token, "wrong-password")


def test_decrypt_corrupted_payload_raises():
    token = encrypt(PLAINTEXT, PASSWORD)
    # Flip a character in the middle of the token
    corrupted = token[:-4] + "XXXX"
    with pytest.raises(ValueError):
        decrypt(corrupted, PASSWORD)


def test_decrypt_invalid_base64_raises():
    with pytest.raises(ValueError, match="Invalid encoded payload"):
        decrypt("!!!not-base64!!!", PASSWORD)


def test_decrypt_too_short_payload_raises():
    import base64
    short_payload = base64.b64encode(b"tooshort").decode()
    with pytest.raises(ValueError, match="too short"):
        decrypt(short_payload, PASSWORD)


def test_encrypt_empty_string():
    token = encrypt("", PASSWORD)
    assert decrypt(token, PASSWORD) == ""


def test_encrypt_unicode():
    unicode_text = "SECRET=caf\u00e9\u2615"
    token = encrypt(unicode_text, PASSWORD)
    assert decrypt(token, PASSWORD) == unicode_text


def test_encrypt_large_payload():
    """Encryption and decryption should work correctly for large inputs."""
    large_text = "KEY=" + "x" * 100_000
    token = encrypt(large_text, PASSWORD)
    assert decrypt(token, PASSWORD) == large_text


def test_decrypt_empty_password_raises():
    """An empty password should raise a ValueError rather than silently producing garbage."""
    token = encrypt(PLAINTEXT, PASSWORD)
    with pytest.raises(ValueError):
        decrypt(token, "")


def test_encrypt_empty_password_raises():
    """Encrypting with an empty password should raise a ValueError."""
    with pytest.raises(ValueError):
        encrypt(PLAINTEXT, "")
