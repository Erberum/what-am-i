import json
import logging
import os
import time
from copy import deepcopy

import cryptography
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
import gzip
import struct
import sys


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
        signature = block[:64]
        public_key = block[64:96]
        cls.verify(block, public_key)
        index = struct.unpack_from('>Q', block, 96)[0]
        previous_hash = block[104:136]
        timestamp = struct.unpack_from('>d', block, 136)[0]
        data = block[144:]
        return Block(data, index, previous_hash, public_key, timestamp, signature)

    def __init__(self, data: bytes, index: int, previous_hash: bytes, public_key: bytes, timestamp: float,
                 signature: bytes = None):
        assert len(previous_hash) == 32, 'Invalid Hash'
        assert len(public_key) == 32, 'Invalid Public Key'

        self.data = data
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.public_key = public_key
        self.signature = signature

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

    def hash(self):
        return sha256(self.__serialize_inner())

    def sign(self, private_key: bytes) -> bytes:
        # Block Format (Signature)
        # Signature (64 bytes)
        # ... Block ...
        self.signature = sign(self.hash(), private_bytes=private_key)

    def serialize(self):
        assert self.signature is not None, 'Block needs to be signed before it can be serialized'
        result = self.signature + self.__serialize_inner()
        self.verify(result, self.public_key)
        return result

    def __repr__(self):
        return f'Block({self.index}, b\'...{str(self.previous_hash[-8:])[2:-1]}\', {self.timestamp}, {self.data})'

    @property
    def signed(self):
        return self.signature is not None


class Blockchain:
    @classmethod
    def load(cls, path: str, create: bool = False):
        if create and not os.path.exists(path):
            blockchain = Blockchain()
            blockchain.add_block_zero()
            return blockchain
        with gzip.open(path, 'rb') as rf:
            return cls.from_dump(rf.read())

    @classmethod
    def from_dump(cls, dump: bytes):
        blockchain = Blockchain()
        while dump:
            block_size = struct.unpack('>I', dump[:4])[0]
            block = dump[4:4 + block_size]
            dump = dump[4 + block_size:]
            blockchain.add_block(block)
        return blockchain

    @classmethod
    def verify(cls, blocks: list):
        prev_block: Block = None
        for block in blocks:
            # General block checks
            assert block.timestamp < time.time()
            if prev_block is None:
                prev_block = block
                assert block.index >= 0
                continue
            # Checks with previous block
            assert block.index == prev_block.index + 1
            assert block.previous_hash == prev_block.hash()
            assert block.timestamp >= prev_block.timestamp

    def __init__(self):
        self.blocks: list[Block] = []

    def add_block(self, block: bytes):
        block_obj = Block.deserialize(block)
        self.blocks.append(block_obj)
        try:
            self.verify(self.blocks[-2:])  # Check with accordance to previous block
        except Exception as e:
            self.blocks.pop()
            raise e

    def add_block_zero(self):
        private_key = generate_private_key()  # Discarded
        public_key = generate_public_key(private_key)
        block_zero = Block(b'', 0, b'0' * 32, public_key, time.time())
        block_zero.sign(private_key)
        self.add_block(block_zero.serialize())

    @property
    def last_block(self):
        return self.blocks[-1]

    @property
    def last_index(self):
        return self.last_block.index

    @property
    def last_hash(self):
        return self.last_block.hash()

    def dump(self) -> bytes:
        result = b''
        for block in self.blocks:
            block_bytes = block.serialize()
            result += struct.pack(f'>I', len(block_bytes))
            result += block_bytes
        return result

    def save(self, path: str):
        with gzip.open(path, 'wb') as wf:
            wf.write(self.dump())

    def get_block(self, index: int):
        # TODO: Binary search for partial blockchain support
        block = self.blocks[index]
        assert block.index == index
        return block


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
    block.sign(private_key)
    Block.verify(block=block.serialize(),
                 public_key=public_key)  # Should not throw an error since signature is correct
    try:
        block.sign(private_key)
        Block.verify(block=block.serialize() + b'2', public_key=public_key)
        raise AssertionError('Signature incorrect, yet Block.verify() didn\'t throw an exception')
    except InvalidSignature:
        pass  # Expected, since block was tinkered with

    # Test block serialization / deserialization
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    block = Block(b'test', 0, b'0' * 32, public_key, time.time())
    block.sign(private_key)
    serialized = block.serialize()
    deserialized = Block.deserialize(serialized)
    assert deserialized.index == block.index
    assert deserialized.previous_hash == block.previous_hash
    assert deserialized.timestamp == block.timestamp
    assert deserialized.data == block.data
    assert deserialized.public_key == block.public_key
    # TODO: Check that can't serialize if not signed
    try:
        Block.deserialize(serialized + b'2')
        raise AssertionError('Signature incorrect, yet Block.deserialize() didn\'t throw an exception')
    except InvalidSignature:
        pass  # Expected, since block was tinkered with

    # Blockchain tests
    blockchain = Blockchain()
    blockchain.add_block_zero()
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    block1 = Block(b'block1', blockchain.last_index + 1, blockchain.last_hash, public_key, time.time())
    block1.sign(private_key)
    blockchain.add_block(block1.serialize())
    block2 = Block(b'block2', blockchain.last_index + 1, blockchain.last_hash, public_key, time.time())
    block2.sign(private_key)
    blockchain.add_block(block2.serialize())
    assert blockchain.get_block(2).data == b'block2'
    try:
        blockchain.get_block(3)
    except IndexError:
        pass  # Expected
    assert len(blockchain.blocks) == 3
    # TODO: Tests for last_index, last_hash, timestamp

    # Blockchain saving / loading tests
    blockchain = Blockchain()
    blockchain.add_block_zero()
    private_key = generate_private_key()
    public_key = generate_public_key(private_key)
    block1 = Block(b'test', blockchain.last_index + 1, blockchain.last_hash, public_key, time.time())
    block1.sign(private_key)
    blockchain.add_block(block1.serialize())
    blockchain.save('test.blockchain')
    blockchain_restored = Blockchain.load('test.blockchain')
    os.remove('test.blockchain')
    assert blockchain_restored.blocks[0].data == blockchain.blocks[0].data
    assert blockchain_restored.blocks[1].data == blockchain.blocks[1].data
    assert blockchain_restored.blocks[0].index == blockchain.blocks[0].index
    assert blockchain_restored.blocks[1].index == blockchain.blocks[1].index
    assert blockchain_restored.blocks[0].data == blockchain.blocks[0].data
    assert blockchain_restored.blocks[1].data == blockchain.blocks[1].data
    assert blockchain_restored.blocks[0].timestamp == blockchain.blocks[0].timestamp
    assert blockchain_restored.blocks[1].timestamp == blockchain.blocks[1].timestamp
    assert blockchain_restored.blocks[0].hash() == blockchain.blocks[0].hash()
    assert blockchain_restored.blocks[1].hash() == blockchain.blocks[1].hash()



