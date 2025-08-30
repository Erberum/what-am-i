import time

import cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
import struct


def generate_private_key() -> bytes:
    return Ed25519PrivateKey.generate().private_bytes_raw()


def generate_public_key(private_bytes: bytes) -> bytes:
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    return private_key.public_key().public_bytes_raw()


def sign(data: bytes, private_bytes: bytes) -> bytes:
    private_key = Ed25519PrivateKey.from_private_bytes(private_bytes)
    return private_key.sign(data)


def verify(data: bytes, signature: bytes, public_bytes: bytes):
    public_key = Ed25519PublicKey.from_public_bytes(public_bytes)
    public_key.verify(signature, data)


def sha256(data: bytes) -> bytes:
    hash_ = hashes.Hash(hashes.SHA256())
    hash_.update(data)
    return hash_.finalize()


class Block:
    @classmethod
    def verify(cls, block: bytes, public_key: bytes):
        signature = block[:64]
        verify(sha256(block[64:]), signature, public_key)

    @classmethod
    def deserialize(cls, block: bytes) -> 'Block':
        public_key = block[64:96]
        cls.verify(block, public_key)
        index = struct.unpack_from('>Q', block, 96)[0]
        previous_hash = block[104:136]
        timestamp = struct.unpack_from('>d', block, 136)[0]
        data = block[144:]
        return Block(data, index, previous_hash, public_key, timestamp)

    def __init__(self, data: bytes, index: int, previous_hash: bytes, public_key: bytes, timestamp: float):
        assert len(previous_hash) == 32, 'Invalid Hash'
        assert len(public_key) == 32, 'Invalid Public Key'

        self.data = data
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.public_key = public_key

    def __serialize_inner(self):
        # Block Format (No signature):
        # Index: Unsigned Long Long (8 bytes)
        # Previous Hash: Bytestring (32 bytes)
        # Public Key: Bytestring (32 bytes)
        # Timestamp: Double (8 bytes)
        # Data: Bytestring
        result = self.public_key
        result += struct.pack('>Q', self.index)
        result += self.previous_hash
        result += struct.pack('>d', self.timestamp)
        result += self.data
        return result

    def serialize(self, private_key: bytes) -> bytes:
        # Block Format (Signature)
        # Signature (64 bytes)
        # ... Block ...
        return sign(sha256(self.__serialize_inner()), private_bytes=private_key) + self.__serialize_inner()

    def __repr__(self):
        return f'Block({self.index}, b\'...{str(self.previous_hash[-8:])[2:-1]}\', {self.timestamp}, {self.data})'


if __name__ == '__main__':
    # Test hashing
    assert sha256(b'test') == sha256(b'test')
    assert sha256(b'test1') != sha256(b'test2')

    # Test signing & verification
    message = b'hello'
    private_key = generate_private_key()
    signature = sign(message, private_key)
    public_key = generate_public_key(private_key)
    verify(message, signature, public_key)  # Should not throw an error since signature is correct
    try:
        verify(message + b'2', signature, public_key)
        raise AssertionError('Signature incorrect, yet verify() didn\'t throw an exception')
    except InvalidSignature:
        pass  # Expected, since message was tinkered with

    # Test block signing & verification
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    block = Block(b'test', 0, b'0' * 32, public_key, time.time())
    Block.verify(block=block.serialize(private_key),
                 public_key=public_key)  # Should not throw an error since signature is correct
    try:
        Block.verify(block=block.serialize(private_key) + b'2', public_key=public_key)
        raise AssertionError('Signature incorrect, yet Block.verify() didn\'t throw an exception')
    except InvalidSignature:
        pass  # Expected, since block was tinkered with

    # Test block serialization / deserialization
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    block = Block(b'test', 0, b'0' * 32, public_key, time.time())
    serialized = block.serialize(private_key)
    deserialized = Block.deserialize(serialized)
    assert deserialized.index == block.index
    assert deserialized.previous_hash == block.previous_hash
    assert deserialized.timestamp == block.timestamp
    assert deserialized.data == block.data
    assert deserialized.public_key == block.public_key
    try:
        Block.deserialize(serialized + b'2')
        raise AssertionError('Signature incorrect, yet Block.deserialize() didn\'t throw an exception')
    except InvalidSignature:
        pass  # Expected, since block was tinkered with
