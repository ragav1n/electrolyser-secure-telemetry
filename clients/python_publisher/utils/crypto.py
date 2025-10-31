from cryptography.hazmat.primitives.ciphers.aead import AESGCM
import os, binascii


def maybe_encrypt(payload_bytes: bytes, key_hex: str | None):
    if not key_hex:
        return payload_bytes
    key = binascii.unhexlify(key_hex)
    nonce = os.urandom(12)
    ct = AESGCM(key).encrypt(nonce, payload_bytes, None)
    return nonce + ct  # prefix nonce


def maybe_decrypt(cipher_bytes: bytes, key_hex: str | None):
    if not key_hex:
        return cipher_bytes
    key = binascii.unhexlify(key_hex)
    nonce, ct = cipher_bytes[:12], cipher_bytes[12:]
    return AESGCM(key).decrypt(nonce, ct, None)
