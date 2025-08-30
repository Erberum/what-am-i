from fastapi import FastAPI

from blockchain import BlockChain

app = FastAPI()

blockchain = BlockChain()


@app.get('/')
async def root():
    return {'test': 'test'}


@app.get('/blockchain/{block_index}')
async def root(block_index: int):
    pass
