from contextlib import asynccontextmanager

from fastapi import FastAPI

from blockchain import BlockChain

app = FastAPI()

BLOCKCHAIN_FILE = '1.blockchain'
blockchain = None


@app.get('/')
async def root():
    return {'test': 'test'}


@app.get('/blockchain/{block_index}')
async def root(block_index: int):
    pass


@asynccontextmanager
async def lifespan(app: FastAPI):
    blockchain = BlockChain.load(BLOCKCHAIN_FILE, create=True)
    yield
    blockchain.save(BLOCKCHAIN_FILE)


app = FastAPI(lifespan=lifespan)
