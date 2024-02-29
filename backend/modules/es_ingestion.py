import time
from elasticsearch.exceptions import ConnectionError
from .docker_manager import *


def es_ingestion(dataframe, index_name='hypothesis_v1'):
    from elasticsearch.helpers import bulk
    elastic_search, localhost = start_es_docker()
    mappings = {

        "properties": {
            "ann_id": {"type": "keyword"},
            "parent_doc_id": {"type": "keyword"},
            "document_uri": {"type": "keyword"},
            "document": {"type": "text", "analyzer": "standard"},
            "tags": {"type": "keyword"},
            "created": {"type": "date"},
            "updated": {"type": "date"},
            "user": {"type": "keyword"},
            "text": {"type": "text", "analyzer": "standard"},
            "date": {"type": "date",
                     "ignore_malformed": True},
            "group": {"type": "keyword"},
            "permissions": {"type": "nested"},
            "target": {"type": "nested"},
            "links": {"type": "nested"},
            "user_info": {"type": "object"},
            "flagged": {"type": "text", "analyzer": "standard"},
            "hidden": {"type": "text", "analyzer": "standard"}

        }
    }
    # Create index if it doesn't exist
    wait_time = 0
    while True:
        try:
            # print(elastic_search.info().body)
            if not elastic_search.indices.exists(index=index_name):
                elastic_search.indices.create(index=index_name,
                                              mappings=mappings)
                elastic_search.indices.refresh(index=index_name)
            break
        except ConnectionError:
            print(f"\rWaiting for ElasticSearch to be ready... {wait_time}s",
                  end="")
            time.sleep(1)
        wait_time += 1

    bulk_data = []
    for i, row in dataframe.iterrows():
        bulk_data.append(
            {
                "_index": "hypothesis_v1",
                "_id": row['ann_id'],
                "_source": {
                    "parent_doc_id": row["parent_doc_id"],
                    "document_uri": row["document_uri"],
                    "document": row["document"],
                    "tags": row["tags"],
                    "created": row["created"],
                    "updated": row["updated"],
                    "user": row["user"],
                    "text": row["text"],
                    "date": row["date"],
                    "group": row["group"],
                    "permissions": row["permissions"],
                    "target": row["target"],
                    "links": row["links"],
                    "user_info": row["user_info"],
                    "flagged": row["flagged"],
                    "hidden": row["hidden"]

                }
            }
        )
    bulk(elastic_search, bulk_data)
    print(f"\nSuccessfully created index {index_name} at {localhost}")
    return elastic_search


def get_es_index(es):
    return es.indices.get_alias().keys()

