"""
STELLA ECDH authentication handshake.
The Quest 1 uses X25519 Diffie-Hellman (libsodium curve25519) for the companion
session key. Derived from Authentication.java (CompanionServer decompile 2026-08-18):
  nativeGenerateKeyPair() -> (public_key, private_key)
  nativeKeyExchange(peer_public_key, private_key) -> shared_secret

Status: STUB — implement after first live capture confirms the handshake flow.
The QuestEscape ble_companion_client.py implements the same exchange in Python;
this module will be a clean port of that implementation.
"""

from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey


def generate_keypair():
    """Generate an X25519 keypair for the STELLA handshake."""
    private_key = X25519PrivateKey.generate()
    public_key = private_key.public_key()
    return private_key, public_key


def key_exchange(private_key, peer_public_key_bytes: bytes) -> bytes:
    """Derive shared secret from our private key + peer's public key bytes."""
    from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PublicKey
    peer_key = X25519PublicKey.from_public_bytes(peer_public_key_bytes)
    return private_key.exchange(peer_key)
