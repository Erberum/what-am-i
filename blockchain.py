import cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey


def generate_private_key() -> bytes:
    return Ed25519PrivateKey.generate().private_bytes_raw()


def generate_public_key(private_bytes: bytes) -> bytes:
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    return private_key.public_key().public_bytes_raw()


def sign(data: bytes, private_bytes: bytes) -> bytes:
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    return private_key.sign(data)


def verify(data: bytes, signature: bytes, public_bytes: bytes) -> bool:
    public_key = Ed25519PublicKey.from_public_bytes(public_bytes)
    try:
        public_key.verify(signature, data)
        return True
    except cryptography.exceptions.InvalidSignature:
        return False


def sha256(data: bytes) -> bytes:
    hash_ = hashes.Hash(hashes.SHA256())
    hash_.update(data)
    return hash_.finalize()


if __name__ == '__main__':
    # Test hashing
    assert sha256(b'test') == sha256(b'test')
    assert sha256(b'test1') != sha256(b'test2')

    # Test signing & verification
    message = b'hello'
    private_key = generate_private_key()
    signature = sign(message, private_key)
    public_key = generate_public_key(private_key)
    assert verify(message, signature, public_key)
    assert not verify(message + b'2', signature, public_key)
