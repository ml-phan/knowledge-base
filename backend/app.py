
from modules.search import search_id
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/search{ann_id}")
async def search(ann_id):
    if ann_id:
        response = search_id(elastic_search, ann_id)
        return response