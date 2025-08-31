import base64


def b64(data: bytes):
    return base64.b64encode(data).decode('utf-8')
