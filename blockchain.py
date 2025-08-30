import cryptography
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

private_key = Ed25519PrivateKey.generate()
data = 'test data'.encode()
signature = private_key.sign(data)
public_key = private_key.public_key()
try:
    public_key.verify(signature, data + b'1')
except cryptography.exceptions.InvalidSignature:
    print('Invalid Signature')
