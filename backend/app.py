import sys
from collections import Counter

from fastapi import FastAPI
from modules.search import *
from modules.data_pipeline import *
from modules.es_ingestion import *
from elasticsearch import Elasticsearch

sys.path.append("modules")
app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Database"}


@app.get("/search_id")
async def search_by_id(ann_id: str):
    localhost = "http://localhost:9200"
    elastic_search = Elasticsearch(localhost)
    if ann_id:
        response = search_id(elastic_search, ann_id)
        return result_format(response).to_json(orient="records")


@app.get("/search_tags")
async def search_by_tags(tags: str):
    localhost = "http://localhost:9200"
    elastic_search = Elasticsearch(localhost)
    if tags:
        response = search_tag(elastic_search, [tags])
        return result_format(response).to_json(orient="records")


@app.get("/search_text")
async def search_by_text(text: str, max_results: int):
    print(text)
    print(max_results)
    localhost = "http://localhost:9200"
    elastic_search = Elasticsearch(localhost)
    if text:
        response = search_documents(elastic_search, text=text,
                                    query_size=max_results)
        return result_format(response).to_json(orient="records")


@app.get("/database_exists")
async def db_exist():
    return database_exists()


@app.get("/dbop")
async def db_op(mostpopulartags: int):
    database_file = list(Path("../data").glob("*document_es*.*"))[-1]
    database = pd.read_pickle(database_file)
    interesting_tags = [tag for tag in database['tags'].sum() if
                        "is:" in tag]
    most_tags = Counter(interesting_tags).most_common(20)
    return {"tags": most_tags}


@app.get("/docker_ready")
async def docker_rdy():
    return is_docker_container_running()


@app.get("/start_es_docker")
async def docker_rdy():
    database = pd.read_pickle(
        r"../data/hypothesis_document_es_20240119_135741.pickle")
    return es_ingestion(database)


@app.get("/update_db")
async def update_database():
    data_pipeline()


if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host="localhost", port=8000)
