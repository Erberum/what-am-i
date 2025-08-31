import base64
import dataclasses
import json
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware

from blockchain import Blockchain
from utils import b64

BLOCKCHAIN_FILE = 'populated.blockchain'
blockchain: Blockchain = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global blockchain
    blockchain = Blockchain.load(BLOCKCHAIN_FILE, create=True)
    yield
    blockchain.save(BLOCKCHAIN_FILE)


app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)


@app.get('/')
async def root():
    return {'test': 'test'}


@app.get('/blockchain/block/{block_index}')
async def get_block(block_index: int):
    try:
        blockchain.get_block(block_index)
    except IndexError:
        raise HTTPException(status_code=404, detail='Block not found')
    return Response(content=blockchain.get_block(block_index).serialize(), media_type='application/octet-stream')


@app.get('/blockchain/last_block')
async def get_last_block():
    return Response(content=blockchain.last_block.serialize(), media_type='application/octet-stream')


@app.get('/api/block/{block_index}')
async def get_block_json(block_index: int):
    try:
        block = blockchain.get_block(block_index)
    except IndexError:
        raise HTTPException(status_code=404, detail='Block not found')
    return {
        'signature_b64': b64(block.signature),
        'index': block.index,
        'previous_hash_b64': b64(block.previous_hash),
        'public_key_b64': b64(block.public_key),
        'timestamp': block.timestamp,
        'data_b64': b64(block.data),
        'sha256_b64': b64(block.hash())
    }


def build_tree(starting_block: int):
    data = get_json(starting_block)
    data['children'] = []
    for proportion, child_data in data['components']:
        data['children'].append(build_tree(child_data['blockchain_index']))
    return data


def get_json(block_index):
    block = blockchain.get_block(block_index)
    return json.loads(block.data.decode())


@app.get('/api/build_tree/{block_index}')
async def get_tree_json(block_index: int):
    return build_tree(block_index)
