import os
import sys
import time
from collections import Counter

from fastapi import FastAPI
from pydantic import BaseModel
from modules.search import *
from modules.data_pipeline import *
from modules.es_ingestion import *
from elasticsearch import Elasticsearch

sys.path.append("modules")
app = FastAPI()


class ResponseModel(BaseModel):
    dataframe: str
    hits: int
    start: int
    end: int


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
        # response = search_tag(elastic_search, [tags])
        search_list = tags.split(" ")
        print(search_list)
        response = search_documents(elastic_search, keywords=tags.split(" "))
        return result_format(response).to_json(orient="records")


@app.get("/search_text")
async def search_by_text(text: str, max_results: int):
    print(text)
    print(max_results)
    localhost = "http://localhost:9200"
    elastic_search = Elasticsearch(localhost)
    if text:
        response = search_term(elastic_search,
                               term=text,
                               result_size=max_results)
        return result_format(response).to_json(orient="records")


@app.get("/search_combine", response_model=ResponseModel)
async def search_by_text(tag: str, term: str, start: int, num_result: int):
    localhost = "http://localhost:9200"
    elastic_search = Elasticsearch(localhost)
    response = search_combine(elastic_search,
                              tags=tag,
                              terms=term,
                              start=start,
                              num=num_result)
    hits = response["hits"]["total"]["value"]
    end = start + num_result
    if start < hits < end:
        num_result = hits - start
        response = search_combine(elastic_search,
                                  tags=tag,
                                  terms=term,
                                  start=start,
                                  num=num_result)
        end = hits
    elif hits < start:
        num_result = min(num_result, hits)
        start = hits - num_result
        response = search_combine(elastic_search,
                                  tags=tag,
                                  terms=term,
                                  start=start,
                                  num=num_result)
        end = hits
    resp_df = result_format(response)
    resp_df_json = resp_df.to_json(orient="records")
    return ResponseModel(dataframe=resp_df_json, hits=hits,
                         start=start, end=end)


@app.get("/database_exists")
async def db_exist():
    return database_exists()


@app.get("/dbop")
async def db_op(mostpopulartags: int):
    database_file = list(find_data_folder().glob("*document_es*.*"))[-1]
    database = pd.read_pickle(database_file)
    # interesting_tags = [tag for tag in database['tags'].sum()]
    start = time.perf_counter()
    interesting_tags = [item for sublist in database['tags'] for item in
                        sublist]
    most_tags = Counter(interesting_tags).most_common(20)
    end = time.perf_counter()
    print(f"Time took to get most_tags {end - start} seconds.")
    return {"tags": most_tags}


@app.get("/docker_ready")
async def docker_rdy():
    return is_docker_container_running()


@app.get("/start_es_docker")
async def docker_rdy():
    database = pd.read_pickle(list(find_data_folder().glob("*document*"))[-1])
    es_ingestion(database)


@app.get("/update_db")
async def update_database():
    data_pipeline()


if __name__ == '__main__':
    import uvicorn

    filename = os.path.splitext(os.path.basename(__file__))[0]
    uvicorn.run(f"{filename}:app", host="localhost", port=8000, reload=False)
