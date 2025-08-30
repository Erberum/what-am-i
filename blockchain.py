import cryptography
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey


# private_key = Ed25519PrivateKey.generate()
# data = 'test data'.encode()
# signature = private_key.sign(data)
# public_key = private_key.public_key()
# try:
#     public_key.verify(signature, data + b'1')
# except cryptography.exceptions.InvalidSignature:
#     print('Invalid Signature')

def sha256(data: bytes) -> bytes:
    hash_ = hashes.Hash(hashes.SHA256())
    hash_.update(data)
    return hash_.finalize()


if __name__ == '__main__':
    # Test stuff
    assert sha256(b'test') == sha256(b'test')
    assert sha256(b'test1') != sha256(b'test2')
